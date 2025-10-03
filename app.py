import streamlit as st
from groq import Groq
import os

# Load Groq API key (set in Streamlit Cloud secrets or environment)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Groq Voice Bot", page_icon="🎤")
st.title("🎤 Groq Voice Bot")
st.write("Ask me anything! You can use your voice or type a question.")

# Text input
user_text = st.text_input("Type your question here:")

# Button to get AI reply
if st.button("Ask"):
    if user_text.strip():
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": user_text}]
            )
            reply = completion.choices[0].message.content
            st.success(reply)

            # Pass reply to frontend for speech (JS)
            st.components.v1.html(
                f"""
                <script>
                var msg = new SpeechSynthesisUtterance("{reply}");
                window.speechSynthesis.speak(msg);
                </script>
                """,
                height=0,
            )

# Simple instructions for voice users
st.markdown("""
👉 For voice: Use your browser’s built-in microphone-to-text (click mic icon in text box if available).  
👉 For accessibility: The bot will read answers aloud automatically.
""")
