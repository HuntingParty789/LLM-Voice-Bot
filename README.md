# LLM-Voice-Bot
#🤖 100x AI Companion
An interactive voice chatbot built with Streamlit, leveraging Groq’s language model and Whisper transcription, combined with Google Text-to-Speech for spoken AI responses.

#Features
Speech-based input via microphone with start/stop controls and silence detection.

Real-time speech-to-text transcription using Groq Whisper model.

Conversational AI powered by Groq’s GPT-OSS-20b model.

Voice responses synthesized on demand using Google’s Text-to-Speech (gTTS).

Chat history maintained within a session.

Simple, user-friendly web interface with text input fallback.

#Setup and Installation
Prerequisites
Python 3.8 or newer

Streamlit

Groq Python SDK with valid API key

gtts for text-to-speech

streamlit_mic_recorder for microphone input handling

#Installation Steps
Clone or download the repository with the app code.

Install required packages:

bash
pip install streamlit groq-api gtts streamlit-mic-recorder
Add your Groq API key securely in Streamlit secrets:

Create a secrets.toml file (or use your cloud provider’s method) with:

text
[secrets]
GROQ_API_KEY = "your_groq_api_key_here"
Running the Application
Run the app locally with:

bash
streamlit run app.py
Open the URL displayed in your browser to interact with the voice chatbot.

#Usage Instructions
Use the microphone button (🎙️) to start speaking; press the stop button (🛑) to stop or rely on silence detection to auto-stop recording.

Transcribed text will appear in the chat, and the AI will respond with text and synthesized voice.

You may also type messages manually in the text input area.

Responses are played back automatically as audio.

#Notes
Silence detection parameters (silence_threshold and silence_duration) help auto-stop recording after 2 seconds of silence.

Audio responses are generated and played via temporary MP3 files.

The app relies on internet connectivity for Groq API calls and Google TTS.

Autoplay audio behavior depends on browser permissions and may require user interaction initially.

#Troubleshooting
Ensure microphone access permission in your browser.

Verify API key correctness and access rights with Groq.

If audio responses do not play automatically, manually pressing play on the audio widget may be necessary due to browser autoplay restrictions.

Update Streamlit and dependencies regularly for best performance.

Future Enhancements
Improve audio playback with in-memory buffers to reduce latency.

Add UI feedback such as loading spinners during transcription and response generation.

Enhance silence detection robustness.

Support multi-language speech input and output.
