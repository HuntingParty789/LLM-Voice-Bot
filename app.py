import streamlit as st
from groq import Groq
import sounddevice as sd
import numpy as np
import tempfile
import wave
import os

# Initialize Groq client (API key must be set in environment variable)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Set page config
st.set_page_config(page_title="Groq Chatbot", page_icon="🤖", layout="wide")

st.title("🤖 Chat with Groq AI")
st.write("Talk using **text** or **voice** 🎙️")

# Store chat history
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
st.write("🎤 Or record your voice:")

if st.button("Start Recording"):
    duration = 5  # seconds
    fs = 44100

    st.write("Recording... Speak now!")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    st.write("Recording stopped.")

    # Save to temp WAV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        wav_path = tmpfile.name
        with wave.open(wav_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(recording.tobytes())

    # Send to Groq STT
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
if st.button("🛑 Stop Conversation"):
    st.session_state["messages"] = []
    st.success("Conversation reset!")
