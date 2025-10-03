import streamlit as st
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms.groq import ChatGroq
from langchain.chains import RetrievalQA
from gtts import gTTS
import tempfile
import speech_recognition as sr

# Replace this string with your *full* resume text
resume_text = """
VIDYANSHU KUMAR SINHA
Summary: Enthusiastic Computer Science graduate with backend dev skills in Python, Flask, FastAPI.
Experienced with APIs, MySQL, GenAI tools, LangChain, open-source LLMs.
B.TECH, CSE (AIML), CV Raman Global University.
Projects: Deep Learning Music Genre Classifier, GenAI Chatbot, Gmail summarizer with n8n.
Intern: Insergo Technologies (Flask API/Ansible automation).
Skills: Python, C, SQL, Docker, Git, Flask, FastAPI, ML/DL, Azure, AWS, OpenAI, HuggingFace, n8n.
"""
# ----------------------------

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_texts([resume_text], embeddings)
groq_llm = ChatGroq(
    groq_api_key="YOUR_GROQ_API_KEY",   # <--- put your key here
    model="mixtral-8x7b-32768"
)
qa_chain = RetrievalQA.from_chain_type(
    llm=groq_llm,
    retriever=vectorstore.as_retriever(),
)

def is_personal_question(q):
    keywords = [
        "your ", "you ", "about you", "background", "resume", "project", "internship",
        "life story", "superpower", "strengths", "grow in", "career"
    ]
    return any(word in q.lower() for word in keywords)

st.title("Ask Vidyanshu Sinha's AI 🤖")
input_mode = st.radio("Select input type:", ('Type', 'Audio'))
question = ""

if input_mode == "Type":
    question = st.text_input("Type your question below")
else:
    audio_file = st.file_uploader("Upload a WAV audio file with your question", type=["wav"])
    if audio_file:
        rec = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = rec.record(source)
            try:
                question = rec.recognize_google(audio)
                st.write(f"You said: {question}")
            except:
                st.warning("Could not understand the audio.")

if st.button("Ask") and question:
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
