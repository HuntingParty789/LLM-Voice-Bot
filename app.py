import streamlit as st
from streamlit_audio_recorder import audio_recorder
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms.groq import ChatGroq
from langchain.chains import RetrievalQA
from gtts import gTTS
import tempfile
import speech_recognition as sr

# Resume text (paste full resume)
resume_text = """
VIDYANSHU KUMAR SINHA
Summary: Enthusiastic Computer Science graduate...
"""

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_texts([resume_text], embeddings)

groq_api_key = st.secrets["groq"]["api_key"]

groq_llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="mixtral-8x7b-32768"
)
qa_chain = RetrievalQA.from_chain_type(
    llm=groq_llm,
    retriever=vectorstore.as_retriever(),
)

def is_personal_question(q: str) -> bool:
    keywords = ["your", "you", "background", "skills", "project", "resume"]
    q = q.lower()
    return any(word in q for word in keywords)

st.title("Groq AI Voicebot with Browser Microphone")

# Audio recorder widget (browser mic, permission managed by browser)
audio_bytes = audio_recorder()

question = ""

if audio_bytes:
    # Use speech_recognition to transcribe recorded audio bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpwav:
        tmpwav.write(audio_bytes)
        tmpwav_path = tmpwav.name
    
    recognizer = sr.Recognizer()
    with sr.AudioFile(tmpwav_path) as source:
        audio_data = recognizer.record(source)
        try:
            question = recognizer.recognize_google(audio_data)
            st.write(f"Transcribed question: {question}")
        except Exception as e:
            st.error(f"Could not transcribe audio: {e}")

# Text input fallback
typed_question = st.text_input("Or type a question here")

if typed_question:
    question = typed_question

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
