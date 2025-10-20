import streamlit as st
from gtts import gTTS
import wikipedia
import pyjokes
import requests
import datetime
import base64
import io
import urllib.parse
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av
import threading

# --- Core Functions ---

def text_to_speech_autoplay(text):
    """Generates speech and returns HTML for an invisible autoplaying audio player."""
    try:
        tts = gTTS(text=text, lang='en')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        b64 = base64.b64encode(mp3_fp.read()).decode()
        audio_html = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        return audio_html
    except Exception as e:
        st.error(f"Error in TTS: {e}")
        return ""

def get_weather(city):
    """Fetches weather information from OpenWeatherMap API."""
    api_key = st.secrets.get("OPENWEATHER_API_KEY")
    if not api_key:
        st.session_state.assistant_response_display = "Weather API key not configured."
        return "Error: Weather API key is not configured."

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={city}&units=metric"
    try:
        response = requests.get(complete_url)
        x = response.json()
        if x.get("cod") != 200:
            return f"Sorry, I couldn't find the weather for {city}. Reason: {x.get('message', 'Unknown error')}."
        main = x["main"]
        temperature = main["temp"]
        description = x["weather"][0]["description"]
        return f"The temperature in {city} is {temperature}°C with {description}."
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def process_command(command):
    """Processes the command and updates the session state."""
    response = "I could not hear you properly or the command is not recognized."
    response_display = response

    if not command:
        response = "Empty command received."
        response_display = response
    elif 'play' in command:
        song = command.replace('play', '').strip()
        search_query = urllib.parse.quote(song)
        youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
        response = f"Here is a link to search for {song} on YouTube."
        response_display = f"Here is a link for '{song}':\n[Click here to watch]({youtube_url})"
    elif 'time' in command:
        time_str = datetime.datetime.now().strftime('%I:%M %p')
        response = f'The current time is {time_str}'
        response_display = response
    elif 'who is' in command:
        person = command.replace('who is', '').strip()
        try:
            info = wikipedia.summary(person, 1)
            response = info
            response_display = response
        except wikipedia.exceptions.PageError:
            response = f"Sorry, I could not find any information on {person}."
            response_display = response
        except wikipedia.exceptions.DisambiguationError:
            response = f"Multiple results for {person}. Please be more specific."
            response_display = response
    elif 'joke' in command:
        joke = pyjokes.get_joke()
        response = joke
        response_display = response
    elif 'weather in' in command:
        parts = command.split('weather in')
        if len(parts) > 1:
            city = parts[1].strip()
            response = get_weather(city)
        else:
            response = "Please specify a city, like: 'weather in London'."
        response_display = response
    elif 'stop' in command or 'exit' in command:
        response = 'Goodbye!'
        response_display = response
        st.session_state.audio_to_play = text_to_speech_autoplay(response)
        st.stop()
    
    st.session_state.last_command = command
    st.session_state.assistant_response = response
    st.session_state.assistant_response_display = response_display
    st.session_state.audio_to_play = text_to_speech_autoplay(response)

# --- WebRTC Audio Processing ---
recognizer = sr.Recognizer()
lock = threading.Lock()
audio_buffer = io.BytesIO()

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        super().__init__()
        self._is_recording = False

    def start(self):
        with lock:
            self._is_recording = True
            audio_buffer.seek(0)
            audio_buffer.truncate(0)

    def stop(self):
        with lock:
            self._is_recording = False
            return self.process_audio()

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        if self._is_recording:
            # Convert audio frame to raw PCM data
            pcm_s16 = frame.to_ndarray(format="s16")
            with lock:
                audio_buffer.write(pcm_s16.tobytes())
        return frame

    def process_audio(self):
        with lock:
            audio_buffer.seek(0)
            audio_data = sr.AudioData(audio_buffer.read(), sample_rate=16000, sample_width=2)
        try:
            command = recognizer.recognize_google(audio_data).lower()
            if 'alexa' in command:
                command = command.replace('alexa', '').strip()
            return command
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Speech recognition request failed: {e}"

# --- Streamlit UI ---
st.set_page_config(page_title="Voice Assistant", layout="centered")

st.title("🗣️ Voice Assistant 'Alexa'")
st.markdown("""
**How to use:**
1. Click **Start** on the component below and **Allow** microphone access.
2. Say your command.
3. Click **Stop**. Alexa will process your command.
""")
st.markdown("---")

# Initialize session state
if 'last_command' not in st.session_state:
    st.session_state.last_command = ""
if 'assistant_response_display' not in st.session_state:
    st.session_state.assistant_response_display = ""
if 'audio_to_play' not in st.session_state:
    st.session_state.audio_to_play = ""

webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"video": False, "audio": True},
    send_audio=True,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

if webrtc_ctx.state.playing and webrtc_ctx.audio_processor:
    st.info("Recording... Click Stop when you are done.")
    webrtc_ctx.audio_processor.start()
elif not webrtc_ctx.state.playing and webrtc_ctx.audio_processor:
    command = webrtc_ctx.audio_processor.stop()
    if command:
        st.session_state.last_command = command
        process_command(command)
        # We need to rerun to display the results and play the audio
        st.rerun()

# Display area for command and response
if st.session_state.last_command or st.session_state.assistant_response_display:
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Your Last Command:**")
        st.info(f"{st.session_state.last_command}")
    with col2:
        st.write("**Alexa's Response:**")
        st.success(f"{st.session_state.assistant_response_display}")
    st.write("---")

# Invisible audio player
if st.session_state.audio_to_play:
    st.components.v1.html(st.session_state.audio_to_play, height=0)
    # Clear the audio after playing to prevent re-playing on every interaction
    st.session_state.audio_to_play = ""

