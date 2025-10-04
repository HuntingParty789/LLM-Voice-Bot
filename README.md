# LLM-Voice-Bot
🤖 100x AI Companion
--> An interactive voice chatbot built with Streamlit, leveraging Groq’s language model and Whisper transcription, combined with Google Text-to-Speech for spoken AI responses.

Features
1. Speech-based input via microphone with start/stop controls and silence detection.

2. Real-time speech-to-text transcription using Groq Whisper model.

3. Conversational AI powered by Groq’s GPT-OSS-20b model.

4. Voice responses synthesized on demand using Google’s Text-to-Speech (gTTS).

5. Chat history maintained within a session.

6. Simple, user-friendly web interface with text input fallback.

Setup and Installation
--> Prerequisites
    Python 3.8 or newer
    Streamlit
    Groq Python SDK with valid API key
    gtts for text-to-speech
    streamlit_mic_recorder for microphone input handling

Installation Steps
--> Clone or download the repository with the app code.

Install required packages:

bash
--> pip install streamlit groq-api gtts streamlit-mic-recorder
    Add your Groq API key securely in Streamlit secrets:

Create a secrets.toml file (or use your cloud provider’s method) with:

-->  text
     [secrets]
     GROQ_API_KEY = "your_groq_api_key_here"
     Running the Application
     Run the app locally with:

bash
-->  streamlit run app.py
     Open the URL displayed in your browser to interact with the voice chatbot.

Usage Instructions
1. Use the microphone button (🎙️) to start speaking; press the stop button (🛑) to stop or rely on silence detection to auto-stop recording.

2. Transcribed text will appear in the chat, and the AI will respond with text and synthesized voice.

3. You may also type messages manually in the text input area.

Notes
1. Silence detection parameters (silence_threshold and silence_duration) help auto-stop recording after 2 seconds of silence.

2. Audio responses are generated and played via temporary MP3 files.

3. The app relies on internet connectivity for Groq API calls and Google TTS.

3. Autoplay audio behavior depends on browser permissions and may require user interaction initially.

Troubleshooting
1. Ensure microphone access permission in your browser.

2. Verify API key correctness and access rights with Groq.

3. If audio responses do not play automatically, manually pressing play on the audio widget may be necessary due to browser autoplay restrictions.

4. Update Streamlit and dependencies regularly for best performance.

Future Enhancements
1. Improve audio playback with in-memory buffers to reduce latency.

2. Add UI feedback such as loading spinners during transcription and response generation.

3. Enhance silence detection robustness.

4. Support multi-language speech input and output.
