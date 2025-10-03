import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import numpy as np
import tempfile
import threading
import queue
import time
import speech_recognition as sr

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from gtts import gTTS

# Paste your full resume text here
resume_text = """
VIDYANSHU KUMAR SINHA

Summary: Enthusiastic Computer Science graduate with solid backend development skills in Python, Flask, and FastAPI.
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
AI Tools – n8n workflow
"""

# Setup embeddings & vectorstore for resume Q&A
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_texts([resume_text], embeddings)

# Load Groq API key from Streamlit secrets
groq_api_key = st.secrets["groq"]["api_key"]

groq_llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="mixtral-8x7b-32768"
)

qa_chain = RetrievalQA.from_chain_type(
    llm=groq_llm,
    retriever=vectorstore.as_retriever()
)

def is_personal_question(q: str) -> bool:
    personal_keywords = [
        "your", "you", "background", "skills", "project", "resume",
        "life story", "superpower", "strengths", "grow"
    ]
    q = q.lower()
    return any(kw in q for kw in personal_keywords)

# For streaming and processing audio frames:
audio_q = queue.Queue()

def audio_callback(frame: av.AudioFrame):
    audio_q.put(frame)
    return frame

def save_audio_and_transcribe():
    frames = []
    while True:
        try:
            frame = audio_q.get(timeout=5)
            frames.append(frame)
        except queue.Empty:
            break

    if not frames:
        return ""

    # Write frames to temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        output_file = tmpfile.name

    # Convert audio frames to numpy array and save as WAV
    sample_rate = frames[0].sample_rate
    audio_array = np.concatenate([f.to_ndarray() for f in frames], axis=1)

    import soundfile as sf  # needs to be in requirements.txt

    sf.write(output_file, audio_array.T, sample_rate)  # transpose for shape

    # Use SpeechRecognition to transcribe WAV
    recognizer = sr.Recognizer()
    with sr.AudioFile(output_file) as source:
        audio = recognizer.record(source)
        try:
            question = recognizer.recognize_google(audio)
        except Exception as e:
            question = ""
    return question

st.title("Groq AI Voicebot with Browser Microphone")

webrtc_ctx = webrtc_streamer(
    key="microphone",
    mode=WebRtcMode.SENDONLY,
    audio_frame_callback=audio_callback,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

question = ""

if st.button("Stop & Transcribe") and webrtc_ctx.state.playing:
    webrtc_ctx.stop()
    # Process audio frames and transcribe
    question = save_audio_and_transcribe()
    if question:
        st.write(f"Transcribed Question: {question}")
    else:
        st.warning("Could not transcribe audio. Please try again.")

typed_question = st.text_input("Or type your question here")

if typed_question:
    question = typed_question

if question and st.button("Ask"):
    with st.spinner("Thinking..."):
        if is_personal_question(question):
            answer = qa_chain.run(question)
        else:
            answer = groq_llm(question)

        st.success(answer)

        tts = gTTS(answer)
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
            tts.save(fp.name)
            st.audio(fp.name)
