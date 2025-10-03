import streamlit as st
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
import os

# Speech-to-text/text-to-speech packages
import speech_recognition as sr
from gtts import gTTS
import tempfile

# ---- Load and Index Resume ----
resume_text = """
VIDYANSHU KUMAR SINHA
Summary: Enthusiastic Computer Science graduate with solid backend development skills in Python, Flask, and FastAPI.
Experienced in building APIs, working with MySQL, GenAI tools like LangChain and open-source LLMs via Ollama.
...
# (Paste complete text from search above here!)
"""

# Initialize embeddings/vectorstore (for simple demo, one doc is enough)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_texts([resume_text], embeddings)
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(temperature=0,openai_api_key="sk-..."), # Use your OpenAI or OpenRouter key
    retriever=vectorstore.as_retriever()
)

def is_personal_q(q):
    """Basic personal question checker."""
    personal_keywords = [
        "about you", "your background", "your skills", "your project", "your experience",
        "your education", "your internship", "your achievement", "your life story",
        "your strengths", "your career"
    ]
    return any(kw in q.lower() for kw in personal_keywords)

# ---- Streamlit UI ----
st.title("Personal AI Voicebot Demo")

st.write("Ask any question about Vidyanshu Sinha (career, skills, projects) or general questions!")

q_option = st.radio("How do you want to ask?", ("Type", "Upload Audio"))
question = ""

if q_option == "Type":
    question = st.text_input("Enter your question here")
else:
    audio_file = st.file_uploader("Upload a WAV file with your question", type=["wav"])
    if audio_file:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            try:
                question = recognizer.recognize_google(audio_data)
                st.write(f"Transcribed: {question}")
            except Exception as e:
                st.error("Could not transcribe audio.")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        answer = ""
        if is_personal_q(question):
            answer = qa_chain.run(question)
        else:
            openai = OpenAI(temperature=0, openai_api_key="sk-...")
            answer = openai(question)
        st.success(answer)
        # TTS for the answer
        tts = gTTS(answer)
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            audio_bytes = open(tmp.name, "rb").read()
            st.audio(audio_bytes, format="audio/mp3")
