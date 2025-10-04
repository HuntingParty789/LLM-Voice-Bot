import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Vidyanshu Voice Chatbot", layout="centered")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Function: Listen from mic with silence detection ---
def listen_from_mic(timeout=5, phrase_time_limit=15):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        st.write("🎙️ Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            return f"API error: {e}"

# --- Function: Get LLM response ---
def get_llm_response(user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # ✅ lightweight & supported
        messages=[
            {"role": "system", "content": "You are Vidyanshu's AI assistant. Respond naturally and conversationally."},
            {"role": "user", "content": user_input},
        ],
    )
    return response.choices[0].message.content

# --- Function: Speak response ---
def speak_text(text):
    tts = gTTS(text=text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tts.save(tmp.name)
        st.audio(tmp.name, format="audio/mp3")
        return tmp.name

# --- Chat UI ---
st.title("🤖 Vidyanshu AI Voice Chat")

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        if "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")

# --- Input box with mic button ---
col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.chat_input("Type your message here...")
with col2:
    if st.button("🎤"):
        spoken_text = listen_from_mic()
        if spoken_text:
            user_input = spoken_text
        else:
            st.warning("Didn't catch that. Please try again.")

# --- Process user message ---
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    bot_reply = get_llm_response(user_input)
    audio_file = speak_text(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply, "audio": audio_file})
    st.experimental_rerun()
