EchoStream 🗣️

An interactive voice assistant that runs entirely in your web browser. Built with Streamlit, EchoStream allows you to get weather updates, search Wikipedia, play music on YouTube, and hear a joke, all with simple voice commands.

<img width="1153" height="798" alt="Screenshot 2025-10-20 211119" src="https://github.com/user-attachments/assets/09ae222f-e0d5-4931-a140-0009cca21154" />
<img width="1502" height="736" alt="Screenshot 2025-10-20 204150" src="https://github.com/user-attachments/assets/99cef27b-d143-4a10-82f9-b05ec2e5ecad" />


✨ Key Features

🗣️ Voice Command Recognition: Hands-free control to interact with the assistant directly in your browser.

🎵 YouTube Integration: Ask it to "play" any song, and it provides an instant search link to YouTube.

☀️ Real-time Weather: Get current weather forecasts for any city in the world using your voice.

🧠 Wikipedia Search: Ask "who is..." to get a concise, spoken summary from Wikipedia.

😂 Joke Teller: Need a laugh? Just ask for a joke, and EchoStream will tell you one.

🌐 Modern & Responsive UI: A clean, attractive, and user-friendly interface powered by Streamlit.

🎤 Browser-Based Audio: Captures your microphone input directly in the browser using streamlit-webrtc, ensuring privacy and ease of use.

🛠️ Tech Stack

EchoStream uses a powerful combination of Python libraries to bring a voice-first experience to the web:

Frontend: Streamlit

Audio Streaming: streamlit-webrtc

Speech Recognition: SpeechRecognition

Text-to-Speech: gTTS (Google Text-to-Speech)

APIs: OpenWeatherMap, Wikipedia

Deployment: Streamlit Community Cloud

🚀 Getting Started

Follow these instructions to get a local copy up and running for development and testing purposes.

Prerequisites

Python 3.9 or higher

pip package manager

An API key from OpenWeatherMap

Installation

Clone the repository:

git clone [https://github.com/your-username/EchoStream.git](https://github.com/your-username/EchoStream.git)
cd EchoStream


Create and activate a virtual environment (recommended):

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`


Install the required packages:

pip install -r requirements.txt


Set up your API Key:

In the root of your project folder, create a new directory named .streamlit.

Inside .streamlit, create a file named secrets.toml.

Add your API key to this file:

OPENWEATHER_API_KEY = "YOUR_SECRET_API_KEY_HERE"


Run the Streamlit application:

streamlit run app.py


Your browser will automatically open with the application running!

🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 License

Distributed under the MIT License. See LICENSE.md for more information.
