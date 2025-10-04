import streamlit as st
from groq import Groq
from gtts import gTTS
from io import BytesIO
from streamlit_mic_recorder import mic_recorder

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Vidyanshu Voice Chat", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

def get_llm_response(user_input):
    with st.spinner("Generating response..."):
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are Vidyanshu's AI assistant. Answer as Vidyanshu Kumar Sinha."},
                {"role": "user", "content": user_input},
            ],
        )
    return response.choices[0].message.content

def speak_text(text):
    tts = gTTS(text=text, lang="en")
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

st.title("🤖 Vidyanshu Voice Chat")

for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        if "audio" in msg:
            # Display audio player with in-memory audio bytes
            st.audio(msg["audio"], format="audio/mp3")

col1, col2 = st.columns([8, 1])

with col1:
    user_input = st.chat_input("Type your message...")

with col2:
    audio = mic_recorder(
        start_prompt="🎙️",
        stop_prompt="🛑",
        just_once=True,
    )
    if audio:
        with st.spinner("Transcribing audio..."):
            audio_bytes = audio["bytes"]
            from tempfile import NamedTemporaryFile
            with NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_bytes)
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

    audio_fp = speak_text(bot_reply)

    # Save bytes in session state so st.audio can play them
    st.session_state.messages.append({"role": "assistant", "content": bot_reply, "audio": audio_fp.read()})
