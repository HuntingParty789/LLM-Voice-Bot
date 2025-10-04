import streamlit as st
from groq import Groq
from gtts import gTTS
import tempfile
import os
import base64
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

# --- Initialize Groq client ---
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Page setup ---
st.set_page_config(page_title="Groq Voice Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 Chat with Groq AI (Voice + Text)")
st.write("Type or Speak to chat with the bot 🎙️\n\n"
         "👉 Use **'vidyanshu'** in your question for persona mode.")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Trigger word processor ---
def process_prompt(user_input: str):
    if "vidyanshu" in user_input.lower():
        return f"Answer as if you are Vidyanshu Kumar Sinha. User asked: {user_input}"
    return user_input

# --- Text-to-Speech ---
def speak_text(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    filename = "reply.mp3"
    tts.save(filename)
    with open(filename, "rb") as f:
        audio_bytes = f.read()
    b64 = base64.b64encode(audio_bytes).decode()
    return f"""
        <audio autoplay controls>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """

# --- Display history ---
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Text input ---
if prompt := st.chat_input("Type your message..."):
    modified_prompt = process_prompt(prompt)
    st.session_state["messages"].append({"role": "user", "content": modified_prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        resp = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=st.session_state["messages"]
        )
        reply = resp.choices[0].message.content
        st.markdown(reply)
        st.markdown(speak_text(reply), unsafe_allow_html=True)

    st.session_state["messages"].append({"role": "assistant", "content": reply})


# --- Voice Recorder with WebRTC ---
st.subheader("🎤 Talk to the bot")

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.frames.append(frame.to_ndarray().tobytes())
        return frame

webrtc_ctx = webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDRECV,
    audio_receiver_size=256,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

if webrtc_ctx.audio_receiver:
    audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
    if audio_frames:
        # Save captured audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            for af in audio_frames:
                f.write(af.to_ndarray().tobytes())
            wav_path = f.name

        # Transcribe with Groq Whisper
        with open(wav_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f
            )
        os.remove(wav_path)

        user_text = transcript.text
        modified_input = process_prompt(user_text)

        st.session_state["messages"].append({"role": "user", "content": modified_input})
        with st.chat_message("user"):
            st.markdown(user_text)

        with st.chat_message("assistant"):
            resp = client.chat.completions.create(
                model="gemma2-9b-it",
                messages=st.session_state["messages"]
            )
            reply = resp.choices[0].message.content
            st.markdown(reply)
            st.markdown(speak_text(reply), unsafe_allow_html=True)

        st.session_state["messages"].append({"role": "assistant", "content": reply})


# --- Reset ---
if st.button("🛑 Reset Conversation"):
    st.session_state["messages"] = []
    st.success("Conversation reset!")
