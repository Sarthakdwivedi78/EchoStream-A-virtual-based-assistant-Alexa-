import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io
import base64
import pywhatkit
import datetime
import wikipedia
import pyjokes
import requests
import time

# --- Core Functions ---

def speak_text(text):
    """Generates audio from text and plays it in the Streamlit app automatically."""
    try:
        # Create an in-memory audio file
        audio_fp = io.BytesIO()
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        # Encode audio to base64
        audio_bytes = audio_fp.read()
        b64 = base64.b64encode(audio_bytes).decode()

        # Create the HTML audio player with autoplay and hide it
        audio_html = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error generating or playing speech: {e}")


def get_weather(city):
    """Fetches weather information from OpenWeatherMap API."""
    if "OPENWEATHER_API_KEY" not in st.secrets:
        return """
        **Weather API Key Not Found!** To use the weather feature, please:
        1. Create a folder named `.streamlit` in your project directory.
        2. Inside it, create a file named `secrets.toml`.
        3. Add your OpenWeatherMap API key to that file like this:
           `OPENWEATHER_API_KEY = "YOUR_KEY_HERE"`
        """
        
    api_key = st.secrets["OPENWEATHER_API_KEY"]
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
    except sr.UnknownValueError:
        st.session_state.assistant_response = "Sorry, I could not understand what you said."
    except sr.RequestError as e:
        st.session_state.assistant_response = f"Could not request results from speech service; {e}"
    except Exception as e:
        st.session_state.assistant_response = f"An unexpected error occurred: {e}"
    finally:
        st.session_state.status_text = "Ready for the next command."


def process_command(command):
    """Processes the command and updates the session state with the response."""
    response = "I could not hear you properly or the command is not recognized."

    if 'play' in command:
        song = command.replace('play', '').strip()
        response = f'Playing {song} on YouTube.'
        st.session_state.speak_queue.append(response)
        try:
            pywhatkit.playonyt(song)
        except Exception as e:
            response = f"Sorry, I couldn't play '{song}'. It might be a restricted video."

    elif 'time' in command:
        time_str = datetime.datetime.now().strftime('%I:%M %p')
        response = f'The current time is {time_str}'
        st.session_state.speak_queue.append(response)

    elif 'who is' in command:
        person = command.replace('who is', '').strip()
        try:
            info = wikipedia.summary(person, 1)
            response = info
            st.session_state.speak_queue.append(response)
        except wikipedia.exceptions.PageError:
            response = f"Sorry, I could not find any information on {person}."
        except wikipedia.exceptions.DisambiguationError:
            response = f"There are multiple results for {person}. Please be more specific."

    elif 'joke' in command:
        joke = pyjokes.get_joke()
        response = joke
        st.session_state.speak_queue.append(response)
    
    elif 'weather' in command:
        city = ""
        if 'weather in' in command:
            city = command.split('weather in')[-1].strip()
        else:
            city = command.replace('weather', '').strip()
        
        if not city:
            response = "You need to specify a city for the weather, for example: 'weather in London'."
        else:
            response = get_weather(city)
        st.session_state.speak_queue.append(response)

    elif 'stop' in command or 'exit' in command:
        response = 'Goodbye!'
        st.session_state.speak_queue.append(response)
        time.sleep(2)
        st.stop()
    
    st.session_state.assistant_response = response


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
if 'greeted' not in st.session_state:
    st.session_state.greeted = False
# A queue to hold responses to be spoken
if 'speak_queue' not in st.session_state:
    st.session_state.speak_queue = []

# --- Button Logic ---
button_text = "Start Listening"
if not st.session_state.greeted:
    button_text = "Say Hello!"

if st.button(button_text, type="primary"):
    if not st.session_state.greeted:
        st.session_state.speak_queue.append("hey wassupp what is in your mind currently")
        st.session_state.greeted = True
        st.session_state.status_text = "Greeting you now! Ready for the first command."
        time.sleep(0.5) 
        st.rerun()
    else:
        st.session_state.last_command = ""
        st.session_state.assistant_response = ""
        with st.spinner('Listening... Please speak.'):
            run_alexa()
        st.rerun()
else:
    st.info(f"Status: {st.session_state.status_text}")

# Display area for command and response
if st.session_state.last_command or st.session_state.assistant_response:
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Your Last Command:**")
        st.write(f"> {st.session_state.last_command}")
    with col2:
        st.write("**Alexa's Response:**")
        st.write(f"> {st.session_state.assistant_response}")
    st.write("---")

# Process the speak queue
if st.session_state.speak_queue:
    # Get the oldest message to speak
    text_to_speak = st.session_state.speak_queue.pop(0)
    speak_text(text_to_speak)

