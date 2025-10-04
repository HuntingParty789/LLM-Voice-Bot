import streamlit as st
from groq import Groq
from audiorecorder import audiorecorder
from gtts import gTTS
import tempfile
import os
import base64

# Initialize Groq client (make sure to set GROQ_API_KEY in env)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Groq Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 Chat with Groq AI (Voice + Text)")
st.write("Talk using **text** or **voice** 🎙️\n\n"
         "👉 Tip: Use the word **'vidyanshu'** in your question if you want the bot to answer as Vidyanshu.")

if "messages" not in st.session_state:
    st.session_state["messages"] = []


# --- Function to detect trigger ---
def process_prompt(user_input: str):
    """Modify behavior if 'vidyanshu' is mentioned."""
    if "vidyanshu" in user_input.lower():
        return f"Answer this question as if you are Vidyanshu Kumar Sinha Summary: Enthusiastic Computer Science graduate with solid backend development skills in Python, Flask, and FastAPI.
Experienced in building APIs, working with MySQL, GenAI tools like LangChain and open-source LLMs via Ollama.
Education
B.TECH, CSE (Specialization in AI&ML) 2021 - 2025
CV RAMAN GLOBAL UNIVERSITY.
Higher Secondary 2019 - 2020
D.A.V PUBLIC SCHOOL
Senior Secondary 2017 - 2018
D.A.V PUBLIC SCHOOL
Projects
1. Music Genre Classification Using Deep Learning (repository)
Developed a scalable backend for Music Genre Classification using deep learning with TensorFlow and Keras, and
exposed the model through a high-performance FastAPI service. Implemented CI/CD pipelines with GitHub Actions,
Docker, and Azure App Service staging slots for zero-downtime deployments.
2. GenAI-Powered Chatbot for Document Search & Text-to-SQL
Built a chatbot using Azure OpenAI, LangChain, and RAG for document retrieval and text-to-SQL conversion. Used Azure
Cognitive Search and OpenAI embeddings for semantic understanding.
3. Gmail Summarizer using n8n
Built a Gmail Summarizer workflow in n8n that automatically fetches incoming emails, applies an LLM-based
summarization step, and delivers concise summaries to the user, reducing email overload and improving productivity.
Internship
Company - Insergo Technologies
Project - Ansible-Powered Configuration Automation API
Responsibility - Developed and deployed a containerized Flask API server for automating last mile configuration
via ansible: Certificate
Certifications
Cisco
1. Cisco Certified Network Associate: Learned and understood about layer 3 networking, routing and switches:
Certificate
Coursera
1. Using Python to Interact with the Operating System: Certificate
Goldsman Sachs
1. Software Engineering Job Simulation: Gained hands-on exposure on how engineers at Goldman Sachs approach
security and system design: Certificate
Skills
Languages - Python, C, C++, SQL
Developer Tools – Git, Git Hub
Framework – Flask, Fast API, REST API
Machine Learning – Deep Learning, NLP, Machine learning Algorithms.
Cloud – AWS (Amazon Web Service), Microsoft Azure
LLM & GenAI Tools – LangChain, OpenAI API (GPT-3.5, GPT-4), HuggingFace, RAG Architecture, Prompt Engineering, FAISS
AI Tools – n8n workflow). User asked: {user_input}"
    return user_input


# --- Text-to-Speech ---
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


# --- Display chat history ---
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
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        response = client.chat.completions.create(
            model="openai/gpt-oss-20B",   # ✅ Updated working model
            messages=st.session_state["messages"]
        )
        reply = response.choices[0].message.content
        message_placeholder.markdown(reply)

        # 🔊 Speak response
        st.markdown(speak_text(reply), unsafe_allow_html=True)

    st.session_state["messages"].append({"role": "assistant", "content": reply})


# --- Voice input ---
st.write("🎤 Record your voice:")
audio = audiorecorder("🎙️ Start Recording", "🛑 Stop Recording")

if len(audio) > 0:
    # Save audio to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        audio.export(f.name, format="wav")
        wav_path = f.name

    with open(wav_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=f
        )
    os.remove(wav_path)

    text_input = transcript.text
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

        # 🔊 Speak response
        st.markdown(speak_text(reply), unsafe_allow_html=True)

    st.session_state["messages"].append({"role": "assistant", "content": reply})


# --- Reset Conversation ---
if st.button("🛑 Reset Conversation"):
    st.session_state["messages"] = []
    st.success("Conversation reset!")
