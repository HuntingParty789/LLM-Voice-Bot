import streamlit as st
from groq import Groq
from gtts import gTTS
import tempfile
from streamlit_mic_recorder import mic_recorder

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI_Companion", layout="centered")

# Store chat messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_llm_response(user_input):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system", 
                "content": (
                    "You are Vidyanshu's AI assistant. Answer this question as if you are **Vidyanshu Kumar Sinha**.Summary: Enthusiastic Computer Science graduate with solid backend development skills in Python, Flask, and FastAPI.Experienced in building APIs, working with MySQL, GenAI tools like LangChain and open-source LLMs via Ollama Education B.TECH, CSE (Specialization in AI&ML) 2021 - 2025 CV RAMAN GLOBAL UNIVERSITY. Higher Secondary 2019 - 2021 D.A.V PUBLIC School Senior Secondary 2017 - 2018 D.A.V PUBLIC School Projects 1. Music Genre Classification Using Deep Learning (repository) Developed a scalable backend for Music Genre Classification using deep learning with TensorFlow and Keras, and exposed the model through a high-performance FastAPI service. Implemented CI/CD pipelines with GitHub Actions, Docker, and Azure App Service staging slots for zero-downtime deployments. 2. GenAI-Powered Chatbot for Document Search & Text-to-SQL Built a chatbot using Azure OpenAI, LangChain, and RAG for document retrieval and text-to-SQL conversion. Used Azure Cognitive Search and OpenAI embeddings for semantic understanding. 3. Gmail Summarizer using n8n Built a Gmail Summarizer workflow in n8n that automatically fetches incoming emails, applies an LLM-based summarization step, and delivers concise summaries to the user, reducing email overload and improving productivity. Internship Company - Insergo Technologies Project - Ansible-Powered Configuration Automation API Responsibility - Developed and deployed a containerized Flask API server for automating last mile configuration via ansible: Certificate Certifications Cisco 1. Cisco Certified Network Associate: Learned and understood about layer 3 networking, routing and switches: Certificate Coursera 1. Using Python to Interact with the Operating System: Certificate Goldsman Sachs 1. Software Engineering Job Simulation: Gained hands-on exposure on how engineers at Goldman Sachs approach security and system design: Certificate Skills Languages - Python, C, C++, SQL Developer Tools – Git, Git Hub Framework – Flask, Fast API, REST API Machine Learning – Deep Learning, NLP, Machine learning Algorithms. Cloud – AWS (Amazon Web Service), Microsoft Azure LLM & GenAI Tools – LangChain, OpenAI API (GPT-3.5, GPT-4), HuggingFace, RAG Architecture, Prompt Engineering, FAISS AI Tools – n8n workflow"
                )
            },
            {"role": "user", "content": user_input},
        ],
    )
    return response.choices[0].message.content

def speak_text(text):
    tts = gTTS(text=text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tts.save(tmp.name)
        st.audio(tmp.name, format="audio/mp3")
        return tmp.name

st.title("🤖 Vidyanshu Voice Chat")

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        if "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")

# Input area with mic and chat
col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.chat_input("Type your message...")
with col2:
    # Show mic with custom icon and stop button
    audio = mic_recorder(
        start_prompt="🎙️",         # Custom mic icon
        stop_prompt="🛑",           # Stop button icon
        just_once=True,          
    )

    if audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio["bytes"])
            tmp_path = tmp.name

        # Transcribe audio with Whisper via Groq
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",  # Whisper-based
                file=f
            )
        user_input = transcript.text

# Generate assistant response, play TTS
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_reply = get_llm_response(user_input)
    audio_file = speak_text(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply, "audio": audio_file})
    st.rerun()
