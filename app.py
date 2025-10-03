import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="Groq Voice Bot", page_icon="🎤")
st.title("🎤 Groq Voice Bot")
st.write("Talk or type to the bot, and it will respond with voice!")

# Initialize Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY") or "your_api_key_here")

# Text input box
user_text_input = st.text_input("Or type your question here:")

# Buttons
col1, col2 = st.columns([1,1])
with col1:
    ask_button = st.button("Ask via Text")
with col2:
    mic_button = st.button("Start Talking")

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

# Function to send text to Groq and speak reply
def ask_bot(user_text):
    if user_text.strip():
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20B",  # Use your supported model
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

# Handle text input
if ask_button and user_text_input.strip():
    ask_bot(user_text_input)

# Handle mic input (using browser Web Speech API)
if mic_button:
    st.components.v1.html(
        f"""
        <button onclick="startListening()">🎙️ Start Talking</button>
        <p id="status"></p>
        <script>
        var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.interimResults = false;

        recognition.onresult = async function(event) {{
            var userText = event.results[0][0].transcript;
            document.getElementById('status').innerHTML = 'You said: ' + userText;

            // Send text to Streamlit backend using Streamlit's URL query hack
            fetch(window.location.href, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ 'user_text': userText }})
            }});
        }}

        function startListening() {{
            recognition.start();
            document.getElementById('status').innerHTML = 'Listening...';
        }}
        </script>
        """,
        height=150,
    )

# Process POST request from JS mic (Streamlit captures with _stcore/forward_request)
import json
if st.query_params():  # crude way to capture POST
    try:
        data = st.query_params()
        if "user_text" in data:
            ask_bot(data["user_text"][0])
    except:
        pass
