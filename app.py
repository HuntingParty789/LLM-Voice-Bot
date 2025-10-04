import streamlit as st
from groq import Groq
from gtts import gTTS
import tempfile

from streamlit_mic_recorder import mic_recorder

# OpenAI client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Vidyanshu Voice Chat", layout="centered")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LLM reply ---
def get_llm_response(user_input):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are Vidyanshu's AI assistant.You are Vidyanshu's AI assistant. Answer this question as if you are **Vidyanshu Kumar Sinha**.Summary: Enthusiastic Computer Science graduate with solid backend development skills in Python, Flask, and FastAPI. Experienced in building APIs, working with MySQL, GenAI tools like LangChain and open-source LLMs via Ollama. Education: B.TECH, CSE (Specialization in AI&ML) 2021 - 2025 CV RAMAN GLOBAL UNIVERSITY. Higher Secondary 2019 - 2020 D.A.V PUBLIC SCHOOL. Projects: 1. Music Genre Classification Using Deep Learning, Developed a scalable backend for Music Genre Classification using deep learning with TensorFlow and Keras, and exposed the model through a high-performance FastAPI service. Implemented CI/CD pipelines with GitHub ActionsDocker, and Azure App Service staging slots for zero-downtime deployments."},
            {"role": "user", "content": user_input},
        ],
    )
    return response.choices[0].message.content

# --- Speak reply ---
def speak_text(text):
    tts = gTTS(text=text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tts.save(tmp.name)
        st.audio(tmp.name, format="audio/mp3")
        return tmp.name

# --- Chat UI ---
st.title("🤖 Vidyanshu Voice Chat")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        if "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")

# --- Input ---
col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.chat_input("Type your message...")
with col2:
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", just_once=True)

    if audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio["bytes"])
            tmp_path = tmp.name

        # Transcribe audio with Whisper
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",  # Whisper-based
                file=f
            )
        user_input = transcript.text

# --- Process ---
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_reply = get_llm_response(user_input)
    audio_file = speak_text(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply, "audio": audio_file})
    st.rerun()

