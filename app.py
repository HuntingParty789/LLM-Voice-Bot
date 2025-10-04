import streamlit as st
from groq import Groq
from gtts import gTTS
import tempfile
import os
import base64
from streamlit_audiorec import st_audiorec

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Groq Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 Chat with Groq AI (Voice + Text)")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Function to detect trigger ---
def process_prompt(user_input: str):
    if "vidyanshu" in user_input.lower():
        return f"Answer this as if you are Vidyanshu Kumar Sinha. User asked: {user_input}"
    return user_input

# --- Text-to-Speech ---
def speak_text(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    filename = "reply.mp3"
    tts.save(filename)
    with open(filename, "rb") as f:
        audio_bytes = f.read()
    b64 = base64.b64encode(audio_bytes).decode()
    return f"""
        <audio autoplay controls>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """

# --- Display chat history ---
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Text input ---
if prompt := st.chat_input("Type your message..."):
    modified_prompt = process_prompt(prompt)
    st.session_state["messages"].append({"role": "user", "content": modified_prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        resp = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=st.session_state["messages"]
        )
        reply = resp.choices[0].message.content
        st.markdown(reply)
        st.markdown(speak_text(reply), unsafe_allow_html=True)

    st.session_state["messages"].append({"role": "assistant", "content": reply})

# --- Voice input (streamlit-audiorec) ---
st.write("🎤 Record your voice and release the button to process:")
wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(wav_audio_data)
        wav_path = f.name

    with open(wav_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=f
        )
    os.remove(wav_path)

    user_text = transcript.text
    modified_input = process_prompt(user_text)
    st.session_state["messages"].append({"role": "user", "content": modified_input})

    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        resp = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=st.session_state["messages"]
        )
        reply = resp.choices[0].message.content
        st.markdown(reply)
        st.markdown(speak_text(reply), unsafe_allow_html=True)

    st.session_state["messages"].append({"role": "assistant", "content": reply})

# --- Reset button ---
if st.button("🛑 Reset Conversation"):
    st.session_state["messages"] = []
    st.success("Conversation reset!")
