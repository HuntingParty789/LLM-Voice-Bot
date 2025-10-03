import streamlit as st
from groq import Groq
from audiorecorder import audiorecorder
import tempfile
import os

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Groq Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 Chat with Groq AI")
st.write("Talk using **text** or **voice** 🎙️")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Display chat history ---
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Text input ---
if prompt := st.chat_input("Type your message..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=st.session_state["messages"]
        )
        reply = response.choices[0].message.content
        message_placeholder.markdown(reply)

    st.session_state["messages"].append({"role": "assistant", "content": reply})

# --- Voice input ---
st.write("🎤 Record your voice:")
audio = audiorecorder("🎙️ Start Recording", "🛑 Stop Recording")

if len(audio) > 0:
    # Save audio to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        audio.export(f.name, format="wav")
        wav_path = f.name

    with open(wav_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=f
        )
    os.remove(wav_path)

    text_input = transcript.text
    st.session_state["messages"].append({"role": "user", "content": text_input})
    with st.chat_message("user"):
        st.markdown(text_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Processing...")

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=st.session_state["messages"]
        )
        reply = response.choices[0].message.content
        message_placeholder.markdown(reply)

    st.session_state["messages"].append({"role": "assistant", "content": reply})

# --- Stop Conversation ---
if st.button("🛑 Reset Conversation"):
    st.session_state["messages"] = []
    st.success("Conversation reset!")
