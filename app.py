import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="Groq Voice Bot", page_icon="🎤")
st.title("🎤 Groq Voice Bot")
st.write("Talk or type to the bot, and it will respond with voice!")

# Initialize Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY") or "your_api_key_here")

# --- TEXT INPUT ---
user_text_input = st.text_input("Or type your question here:")

if st.button("Ask via Text"):
    if user_text_input.strip():
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model="mixtral-8x7b-32768",   # ✅ stable Groq model
                messages=[{"role": "user", "content": user_text_input}]
            )
            reply = completion.choices[0].message.content
            st.success(reply)

            # Speak reply in browser
            st.components.v1.html(
                f"""
                <script>
                var msg = new SpeechSynthesisUtterance({repr(reply)});
                msg.lang = "en-US";
                window.speechSynthesis.speak(msg);
                </script>
                """,
                height=0,
            )

# --- VOICE INPUT (Browser Mic) ---
st.markdown("### 🎙️ Voice Input")
st.components.v1.html(
    f"""
    <style>
      #status {{
        color: white;
        font-weight: bold;
        margin-top: 10px;
      }}
      button {{
        background: #6c5ce7;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        margin: 5px;
        cursor: pointer;
      }}
    </style>

    <button onclick="startListening()">🎙️ Start Talking</button>
    <button onclick="stopSpeech()">⏹️ Stop</button>
    <p id="status">Click Start Talking...</p>

    <script>
    var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onresult = async function(event) {{
        var userText = event.results[0][0].transcript;
        document.getElementById('status').innerHTML = "You said: " + userText;

        // Call Streamlit backend with fetch API
        const response = await fetch('/ask', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ 'text': userText }})
        }});
        const data = await response.json();
        var reply = data.reply;

        document.getElementById('status').innerHTML += "<br>Bot: " + reply;

        // Speak reply
        var msg = new SpeechSynthesisUtterance(reply);
        msg.lang = "en-US";
        window.speechSynthesis.speak(msg);
    }}

    function startListening() {{
        recognition.start();
        document.getElementById('status').innerHTML = "🎤 Listening...";
    }}

    function stopSpeech() {{
        window.speechSynthesis.cancel();
        document.getElementById('status').innerHTML = "⏹️ Conversation stopped.";
    }}
    </script>
    """,
    height=300,
)
