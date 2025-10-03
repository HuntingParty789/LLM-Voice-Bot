import streamlit as st
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms.groq import ChatGroq
from langchain.chains import RetrievalQA
from gtts import gTTS
import tempfile
import speech_recognition as sr

# --- Your full resume text here ---
resume_text = """
VIDYANSHU KUMAR SINHA
Summary: Enthusiastic Computer Science graduate with backend dev skills Python, Flask, FastAPI.
Experienced with APIs, MySQL, GenAI.
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
...
"""  # Paste full resume

# --- Setup Embeddings and Vectorstore ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_texts([resume_text], embeddings)

# --- Get Groq API key from Streamlit secrets ---
groq_api_key = st.secrets["groq"]["api_key"]

# --- Initialize Groq LLM and RAG QA chain ---
groq_llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="mixtral-8x7b-32768"
)
qa_chain = RetrievalQA.from_chain_type(
    llm=groq_llm,
    retriever=vectorstore.as_retriever(),
)

# --- Personal Question Detector (simple keywords) ---
def is_personal_question(q: str) -> bool:
    keywords = ["your", "you", "background", "skills", "project", "intern", "resume", "life story"]
    q = q.lower()
    return any(word in q for word in keywords)

# --- Streamlit UI ---
st.title("Simple Groq Voicebot for Vidyanshu")

input_mode = st.radio("Input method:", ["Type", "Upload Audio"])

question = ""

if input_mode == "Type":
    question = st.text_input("Enter your question")

else:
    audio_file = st.file_uploader("Upload WAV audio (your question)", type=["wav"])
    if audio_file:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
            try:
                question = recognizer.recognize_google(audio)
                st.write(f"Transcribed: {question}")
            except Exception:
                st.error("Unable to transcribe audio.")

if st.button("Ask") and question:
    with st.spinner("Processing..."):
        if is_personal_question(question):
            answer = qa_chain.run(question)
        else:
            answer = groq_llm(question)
        st.success(answer)
        tts = gTTS(answer)
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
            tts.save(fp.name)
            st.audio(fp.name)
