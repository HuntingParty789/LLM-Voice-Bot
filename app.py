import streamlit as st
from groq import Groq
import os

# Initialize Groq client (API key can come from Streamlit secrets or env var)
client = Groq(api_key=os.getenv("GROQ_API_KEY") or "your_api_key_here")

st.set_page_config(page_title="Groq Voice Bot", page_icon="🎤")
st.title("🎤 Groq Voice Bot")
st.write("Ask me anything! Type your question, and I’ll reply with both text and voice.")

# Text input
user_text = st.text_input("Type your question here:")

# Ask button
if st.button("Ask"):
    if user_text.strip():
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20B",  # or openai/gpt-oss-120B
                messages=[{"role": "user", "content": user_text}]
            )
            reply = completion.choices[0].message.content
            st.success(reply)

            # Pass reply to frontend for speech
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
