import streamlit as st
from groq import Groq
import os
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import queue
import av
import numpy as np
import tempfile
import soundfile as sf

st.set_page_config(page_title="Groq Voice Bot", page_icon="🎤")
st.title("🎤 Groq Voice Bot with Microphone")
st.write("Talk to the bot using your microphone and get spoken answers!")

# Initialize Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY") or "your_api_key_here")

# Audio Queue
audio_queue = queue.Queue()

# Audio processor class
class AudioProcessor(AudioProcessorBase):
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        audio_queue.put(audio)
        return frame

# Start microphone
webrtc_streamer(key="mic", mode=WebRtcMode.SENDONLY, audio_processor_factory=AudioProcessor)

if st.button("Ask"):
    if not audio_queue.empty():
        # Save recorded audio to temp file
        audio_data = []
        while not audio_queue.empty():
            audio_data.append(audio_queue.get())
        audio_np = np.concatenate(audio_data, axis=1).T
        with tempfile.NamedTemporaryFile(suffix=".wav") as f:
            sf.write(f.name, audio_np, 48000)
            f.flush()
            st.audio(f.name, format="audio/wav")
            # TODO: Send audio file to Groq STT (Whisper) to get text
            # For now, just placeholder
            user_text = "This is placeholder text from audio."

        # Send to Groq LLM
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20B",
                messages=[{"role": "user", "content": user_text}]
            )
            reply = completion.choices[0].message.content
            st.success(reply)

            # Speak reply
            st.components.v1.html(
                f"""
                <script>
                var msg = new SpeechSynthesisUtterance({repr(reply)});
                window.speechSynthesis.speak(msg);
                </script>
                """,
                height=0,
            )

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
