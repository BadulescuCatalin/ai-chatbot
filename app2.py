import streamlit as st
import os
import base64
import fitz  # PyMuPDF
from dotenv import load_dotenv
import google.generativeai as genai

from llama_index.core import Document
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding  # Local model for semantic chunking


# ---------------------- Streamlit Config ----------------------
st.set_page_config(page_title="Chatbot", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #1d1e2c; color: #e0e0e0; }
        .css-18e3th9 { background-color: #1d1e2c; }
        .css-1d391kg { color: #e0e0e0; }
        .block-container { padding-top: 2rem; }
    </style>
    <h2 style='text-align: center; color: #B388EB;'>Chatbot</h2>
""", unsafe_allow_html=True)

# ---------------------- Sidebar ----------------------
with st.sidebar:
    st.image("images/gemini_avatar.png", width=150)
    st.markdown("### Operation Tools")

    if st.button("Clear History"):
        st.session_state.clear()

    uploaded_files = st.file_uploader(
        "Choose one or multiple data files",
        type=["pdf"],
        accept_multiple_files=True
    )

# ---------------------- Gemini Model Initialization ----------------------
@st.cache_resource
def initialize_model():
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    system_prompt = """
        You are a helpful assistant specialized in banking document verification.
        Analyze the uploaded PDF files and extract relevant anomalies or issues.
        Provide a short summary, and a bullet list with line numbers if relevant.
    """
    return model.start_chat(history=[{"role": "user", "parts": [system_prompt]}])

# ---------------------- Semantic Chunking ----------------------
def semantic_chunking(text_content, threshold=85):
    embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
    splitter = SemanticSplitterNodeParser(
        buffer_size=1,
        breakpoint_percentile_threshold=threshold,
        embed_model=embed_model
    )
    chunks = [node.get_content() for node in splitter.get_nodes_from_documents([Document(text=text_content)])]
    return chunks

# ---------------------- Print Chunks to Terminal ----------------------
def print_chunks_to_terminal(chunks):
    print("\n--- SEMANTIC CHUNKS ---\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}:\n{chunk}\n{'-'*60}")

# ---------------------- Display PDF ----------------------
def display_pdf(uploaded_file):
    base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="680" height="958" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# ---------------------- Extract PDF Text ----------------------
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.getvalue(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# ---------------------- Initialize Chat ----------------------
if "chat" not in st.session_state:
    st.session_state.chat = initialize_model()

# ---------------------- Handle Uploaded PDF ----------------------
if uploaded_files:
    file_names = [f.name for f in uploaded_files]
    selected_file_name = st.selectbox("Choose a case to view", options=file_names)

    if st.session_state.get("selected_file_name") != selected_file_name:
        st.session_state.selected_file_name = selected_file_name
        st.session_state.pdf_text = None
        st.session_state.chunks = None

    selected_file = next(f for f in uploaded_files if f.name == selected_file_name)

    if "pdf_text" not in st.session_state or st.session_state.pdf_text is None:
        st.session_state.pdf_text = extract_text_from_pdf(selected_file)

    if "chunks" not in st.session_state or st.session_state.chunks is None:
        with st.spinner("Performing semantic chunking..."):
            st.session_state.chunks = semantic_chunking(st.session_state.pdf_text)
            print_chunks_to_terminal(st.session_state.chunks)

    st.markdown("### Preview Document")
    display_pdf(selected_file)

# ---------------------- Chat Interface ----------------------
avatars = {
    "assistant": "images/gemini_avatar.png",
    "user": "images/user_avatar.png"
}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatars.get(msg["role"], None)):
        st.write(msg["content"])

# ---------------------- Run Gemini Query ----------------------
def run_query(input_text):
    try:
        if st.session_state.get("chunks"):
            context = "\n\n".join(st.session_state.chunks[:5])
            full_input = f"{input_text}\n\nRelevant document content:\n{context}"
        else:
            full_input = input_text

        response = st.session_state.chat.send_message(full_input)
        return response.text if response else "Error"
    except Exception as e:
        return f"Error: {e}"

# ---------------------- Chat Input ----------------------
if prompt := st.chat_input("Enter your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=avatars["user"]):
        st.write(prompt)

    with st.chat_message("assistant", avatar=avatars["assistant"]):
        with st.spinner("Thinking..."):
            response = run_query(prompt)
            st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})