import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="Groq Voice Bot", page_icon="🎤")
st.title("🎤 Groq Voice Bot")
st.write("Talk to me using your microphone and get spoken answers instantly!")

# Initialize Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY") or "your_api_key_here")

# Instructions
st.info("Click 'Start Talking' to speak. Your question will be sent automatically, and the bot will reply with voice.")

# Buttons
if st.button("Start Talking"):
    # Inject HTML/JS for browser mic + TTS
    st.components.v1.html(
        f"""
        <button onclick="startListening()">🎙️ Start Talking</button>
        <button onclick="stopSpeech()">⏹️ Stop</button>
        <p id="status"></p>
        <script>
        var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.interimResults = false;

        recognition.onresult = async function(event) {{
            var userText = event.results[0][0].transcript;
            document.getElementById('status').innerHTML = 'You said: ' + userText;

            // Send text to Streamlit backend
            const response = await fetch('/_stcore/forward_request', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{ 'user_text': userText }})
            }});
            // For demo, we just speak user text back
            var reply = "Processing...";  // Replace with backend reply if using API endpoint
            var msg = new SpeechSynthesisUtterance(reply);
            window.speechSynthesis.speak(msg);
        }}

        function startListening() {{
            recognition.start();
            document.getElementById('status').innerHTML = 'Listening...';
        }}

        function stopSpeech() {{
            window.speechSynthesis.cancel();
            document.getElementById('status').innerHTML = 'Conversation stopped.';
        }}
        </script>
        """,
        height=300,
    )
