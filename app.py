import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="Groq Voice Bot", page_icon="🎤")
st.title("🎤 Groq Voice Bot (User-Friendly)")
st.write("Upload a voice note or type your question. The bot will respond with text and speech!")

# Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY") or "your_api_key_here")

# Voice input
uploaded_file = st.file_uploader("Upload a voice recording (wav/m4a/ogg)", type=["wav","m4a","ogg"])

user_text = st.text_input("Or type your question here:")

# Ask button
if st.button("Ask"):
    if uploaded_file:
        # Send audio file to Groq Whisper STT
        st.info("Transcribing audio...")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=uploaded_file
        )
        user_text = transcription.text
        st.write(f"**You said:** {user_text}")

    if user_text.strip():
        st.info("Thinking...")
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20B",
            messages=[{"role": "user", "content": user_text}]
        )
        reply = completion.choices[0].message.content
        st.success(reply)

        # Speak reply in browser
        st.components.v1.html(
            f"""
            <script>
            var msg = new SpeechSynthesisUtterance({repr(reply)});
            window.speechSynthesis.speak(msg);
            </script>
            """,
            height=0,
        )

# Stop button
if st.button("⏹️ Stop"):
    st.components.v1.html(
        """
        <script>
        window.speechSynthesis.cancel();
        </script>
        """,
        height=0,
    )
    st.info("Conversation stopped.")
