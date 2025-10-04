import streamlit as st
from groq import Groq
from gtts import gTTS
import tempfile
from streamlit_mic_recorder import mic_recorder

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Vidyanshu Voice Chat", layout="centered")

# Store chat messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_llm_response(user_input):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system", 
                "content": (
                    "You are Vidyanshu's AI assistant. Answer as Vidyanshu Kumar Sinha. "
                    "Summary: Enthusiastic CSE graduate, backend dev in Python, Flask, FastAPI. "
                    "Skilled in MySQL, GenAI tools, open-source LLM, APIs, n8n, CI/CD, Azure, Ansible automation, "
                    "certified in networking, Python, software engineering."
                )
            },
            {"role": "user", "content": user_input},
        ],
    )
    return response.choices[0].message.content

def speak_text(text):
    tts = gTTS(text=text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tts.save(tmp.name)
        st.audio(tmp.name, format="audio/mp3")
        return tmp.name

st.title("🤖 Vidyanshu Voice Chat")

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        if "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")

# Input area with mic and chat
col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.chat_input("Type your message...")
with col2:
    # Show mic with custom icon and stop button
    audio = mic_recorder(
        start_prompt="🎙️",         # Custom mic icon
        stop_prompt="🛑",           # Stop button icon
        just_once=True,
        silence_threshold=-40,      # dB for silence detection (adjust as needed)
        silence_duration=2          # seconds before auto-stop (2s)
    )

    if audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio["bytes"])
            tmp_path = tmp.name

        # Transcribe audio with Whisper via Groq
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",  # Whisper-based
                file=f
            )
        user_input = transcript.text

# Generate assistant response, play TTS
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_reply = get_llm_response(user_input)
    audio_file = speak_text(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply, "audio": audio_file})
    st.rerun()
