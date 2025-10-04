import streamlit as st
import speech_recognition as sr
from groq import Groq
from gtts import gTTS
import os, base64, tempfile

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Groq Voicebot", page_icon="🎤", layout="wide")
st.title("🎤 Groq Hands-Free Voicebot")
st.write("👉 Just **speak**. When you pause for ~2 seconds, the bot will reply automatically.\n"
         "Use the word **'vidyanshu'** if you want the bot to answer as Vidyanshu.")

if "messages" not in st.session_state:
    st.session_state["messages"] = []


def process_prompt(user_input: str):
    """Modify behavior if 'vidyanshu' is mentioned."""
    if "vidyanshu" in user_input.lower():
        return f"Answer this question as if you are Vidyanshu Kumar Sinha (a final-year B.Tech student in CSE AI & ML at CV Raman Global University). User asked: {user_input}"
    return user_input


def speak_text(text, lang="en"):
    """Convert text to speech and return HTML audio player."""
    tts = gTTS(text=text, lang=lang)
    filename = "reply.mp3"
    tts.save(filename)

    with open(filename, "rb") as f:
        audio_bytes = f.read()

    b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
        <audio autoplay controls>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    return audio_html


# --- Chat history ---
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# --- Start listening button ---
if st.button("🎙️ Start Talking"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now (auto-stops on 2s silence)")
        r.pause_threshold = 2   # <-- silence detection
        audio_data = r.listen(source)

        try:
            text_input = r.recognize_google(audio_data)
            modified_input = process_prompt(text_input)

            st.session_state["messages"].append({"role": "user", "content": modified_input})
            with st.chat_message("user"):
                st.markdown(text_input)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Processing...")

                response = client.chat.completions.create(
                    model="openai/gpt-oss-20B",
                    messages=st.session_state["messages"]
                )
                reply = response.choices[0].message.content
                message_placeholder.markdown(reply)

                # 🔊 Speak reply
                st.markdown(speak_text(reply), unsafe_allow_html=True)

            st.session_state["messages"].append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"Error: {e}")


# --- Reset ---
if st.button("🛑 Reset Conversation"):
    st.session_state["messages"] = []
    st.success("Conversation reset!")
