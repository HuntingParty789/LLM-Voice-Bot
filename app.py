import streamlit as st
from groq import Groq
from gtts import gTTS
import tempfile
from streamlit_mic_recorder import mic_recorder
import base64

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Vidyanshu Voice Chat", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

def get_llm_response(user_input):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are Vidyanshu's AI assistant. Answer this question as if you are **Vidyanshu Kumar Sinha**.Summary: Enthusiastic Computer Science graduate with solid backend development skills in Python, Flask, and FastAPI.Experienced in building APIs, working with MySQL, GenAI tools like LangChain and open-source LLMs via Ollama Education B.TECH, CSE (Specialization in AI&ML) 2021 - 2025 CV RAMAN GLOBAL UNIVERSITY. Higher Secondary 2019 - 2021 D.A.V PUBLIC School Senior Secondary 2017 - 2018 D.A.V PUBLIC School Projects 1. Music Genre Classification Using Deep Learning (repository) Developed a scalable backend for Music Genre Classification using deep learning with TensorFlow and Keras, and exposed the model through a high-performance FastAPI service. Implemented CI/CD pipelines with GitHub Actions, Docker, and Azure App Service staging slots for zero-downtime deployments. 2. GenAI-Powered Chatbot for Document Search & Text-to-SQL Built a chatbot using Azure OpenAI, LangChain, and RAG for document retrieval and text-to-SQL conversion. Used Azure Cognitive Search and OpenAI embeddings for semantic understanding. 3. Gmail Summarizer using n8n Built a Gmail Summarizer workflow in n8n that automatically fetches incoming emails, applies an LLM-based summarization step, and delivers concise summaries to the user, reducing email overload and improving productivity. Internship Company - Insergo Technologies Project - Ansible-Powered Configuration Automation API Responsibility - Developed and deployed a containerized Flask API server for automating last mile configuration via ansible: Certificate Certifications Cisco 1. Cisco Certified Network Associate: Learned and understood about layer 3 networking, routing and switches: Certificate Coursera 1. Using Python to Interact with the Operating System: Certificate Goldsman Sachs 1. Software Engineering Job Simulation: Gained hands-on exposure on how engineers at Goldman Sachs approach security and system design: Certificate Skills Languages - Python, C, C++, SQL Developer Tools – Git, Git Hub Framework – Flask, Fast API, REST API Machine Learning – Deep Learning, NLP, Machine learning Algorithms. Cloud – AWS (Amazon Web Service), Microsoft Azure LLM & GenAI Tools – LangChain, OpenAI API (GPT-3.5, GPT-4), HuggingFace, RAG Architecture, Prompt Engineering, FAISS AI Tools – n8n workflow"},
            {"role": "user", "content": user_input},
        ],
    )
    return response.choices[0].message.content

def speak_text(text):
    tts = gTTS(text=text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tts.save(tmp.name)
        return tmp.name

def get_audio_html(path):
    audio_bytes = open(path, "rb").read()
    b64 = base64.b64encode(audio_bytes).decode()
    html = f"""
    <audio id="audio" autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    <script>
        var audio = document.getElementById('audio');
        audio.play().catch(e => console.log('Autoplay prevented', e));
    </script>
    """
    return html

st.title("🤖 Vidyanshu Voice Chat")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        if "audio" in msg:
            st.markdown(get_audio_html(msg["audio"]), unsafe_allow_html=True)

col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.chat_input("Type your message...")
with col2:
    audio = mic_recorder(
        start_prompt="🎙️",    # Mic icon
        stop_prompt="🛑",     # Stop button
        just_once=True        # Record only once per click
    )
    if audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio["bytes"])
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=f
            )
        user_input = transcript.text

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_reply = get_llm_response(user_input)
    audio_file = speak_text(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply, "audio": audio_file})
