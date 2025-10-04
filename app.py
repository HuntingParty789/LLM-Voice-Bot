import streamlit as st
from groq import Groq
from gtts import gTTS
import tempfile

from streamlit_mic_recorder import mic_recorder

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Vidyanshu Voice Chat", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

def get_llm_response(user_input):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "...Your system prompt here..."},
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

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        if "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")

col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.chat_input("Type your message...")
with col2:
    audio = mic_recorder(
        start_prompt="🎙️",  # Change this to preferred mic icon
        # stop_prompt is omitted to remove stop button
        just_once=True,
        # If the package supports silence detection:
        silence_threshold=-40,  # Adjust as needed
        silence_duration=2      # Silence duration in seconds
    )
    if audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio["bytes"])
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=f
            )
        user_input = transcript.text

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_reply = get_llm_response(user_input)
    audio_file = speak_text(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply, "audio": audio_file})
    st.rerun()
