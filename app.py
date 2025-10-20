import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import wikipedia
import pyjokes
import requests
import datetime
import base64
import io
import urllib.parse

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
        print(f"Error in TTS: {e}")
        return "" # Return empty string on failure

def get_weather(city):
    """Fetches weather information from OpenWeatherMap API."""
    api_key = st.secrets.get("OPENWEATHER_API_KEY")
    if not api_key:
        st.session_state.assistant_response_display = "Weather API key is not configured. Please add it to your secrets."
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
        return f"An error occurred while fetching weather data: {e}"

def run_alexa():
    """The main function to listen, process, and respond."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        command = recognizer.recognize_google(audio).lower()
        if 'alexa' in command:
            command = command.replace('alexa', '').strip()
        st.session_state.last_command = command
        
        process_command(command)

    except sr.WaitTimeoutError:
        st.session_state.assistant_response = "I didn't hear anything. Please try again."
        st.session_state.assistant_response_display = st.session_state.assistant_response
    except sr.UnknownValueError:
        st.session_state.assistant_response = "Sorry, I could not understand what you said."
        st.session_state.assistant_response_display = st.session_state.assistant_response
    except sr.RequestError as e:
        st.session_state.assistant_response = f"Could not request results from speech service; {e}"
        st.session_state.assistant_response_display = st.session_state.assistant_response
    except Exception as e:
        st.session_state.assistant_response = f"An unexpected error occurred: {e}"
        st.session_state.assistant_response_display = st.session_state.assistant_response
    finally:
        st.session_state.status_text = "Ready for the next command."

def process_command(command):
    """Processes the command and updates the session state."""
    response = "I could not hear you properly or the command is not recognized."
    response_display = response

    if 'play' in command:
        song = command.replace('play', '').strip()
        # URL encode the song title to handle spaces and special characters
        search_query = urllib.parse.quote(song)
        youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
        response = f"Here is a link to search for {song} on YouTube."
        # Create a clickable markdown link for the UI
        response_display = f"Here is a link to search for '{song}' on YouTube:\n[Click here to watch]({youtube_url})"
    
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
            response = f"There are multiple results for {person}. Please be more specific."
            response_display = response

    elif 'joke' in command:
        joke = pyjokes.get_joke()
        response = joke
        response_display = response
    
    elif 'weather in' in command:
        # More robustly extract city name after "weather in"
        parts = command.split('weather in')
        if len(parts) > 1:
            city = parts[1].strip()
            response = get_weather(city)
        else:
            response = "You need to specify a city for the weather, for example: 'weather in London'."
        response_display = response

    elif 'stop' in command or 'exit' in command:
        response = 'Goodbye!'
        response_display = response
        st.session_state.audio_to_play = text_to_speech_autoplay(response)
        st.stop()
    
    st.session_state.assistant_response = response
    st.session_state.assistant_response_display = response_display
    st.session_state.audio_to_play = text_to_speech_autoplay(response)

# --- Streamlit UI ---

st.set_page_config(page_title="Voice Assistant", layout="centered")

st.title("🗣️ Voice Assistant 'Alexa'")
st.markdown("""
**How to use:**
1.  Click the button below to start.
2.  Your browser will ask for **microphone permission**. Please **Allow** it.
3.  Say a command like:
    * `Alexa, play happy birthday song`
    * `Alexa, who is Albert Einstein?`
    * `Alexa, what's the weather in New York?`
""")
st.markdown("---")

# Initialize session state variables
if 'status_text' not in st.session_state:
    st.session_state.status_text = "Click the button to give a command."
if 'last_command' not in st.session_state:
    st.session_state.last_command = ""
if 'assistant_response' not in st.session_state:
    st.session_state.assistant_response = ""
if 'assistant_response_display' not in st.session_state:
    st.session_state.assistant_response_display = ""
if 'greeted' not in st.session_state:
    st.session_state.greeted = False
if 'audio_to_play' not in st.session_state:
    st.session_state.audio_to_play = ""

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

# --- Button Logic ---
button_text = "Start Listening"
if not st.session_state.greeted:
    button_text = "Say Hello!"

if st.button(button_text, type="primary", use_container_width=True):
    if not st.session_state.greeted:
        st.session_state.greeted = True
        st.session_state.status_text = "Ready for the first command."
        st.session_state.audio_to_play = text_to_speech_autoplay("hey wassupp what is in your mind currently")
        st.rerun()
    else:
        st.session_state.last_command = ""
        st.session_state.assistant_response_display = ""
        st.session_state.audio_to_play = "" # Clear previous audio
        with st.spinner('Listening... Please speak.'):
            run_alexa()
        st.rerun()
else:
    st.info(f"Status: {st.session_state.status_text}")

# Invisible audio player
if st.session_state.audio_to_play:
    st.components.v1.html(st.session_state.audio_to_play, height=0)

