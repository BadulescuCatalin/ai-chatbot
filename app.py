import streamlit as st
import os
import base64
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd

# Page config
st.set_page_config(page_title="Chatbot", layout="wide")

# Styling and headers
st.markdown("""
    <style>
        .main { background-color: #1d1e2c; color: #e0e0e0; }
        .css-18e3th9 { background-color: #1d1e2c; }
        .css-1d391kg { color: #e0e0e0; }
        .block-container { padding-top: 2rem; }
    </style>
    <h2 style='text-align: center; color: #B388EB;'>Chatbot</h2>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("images/gemini_avatar.png", width=150)
    st.markdown("### Operation Tools")
    st.checkbox("Activate Operation Agent", value=True)
    if st.button("Clear History"):
        st.session_state.clear()
    uploaded_files = st.file_uploader(
        "Choose one or multiple data files",
        type=["pdf", "msg", "png"],
        accept_multiple_files=True
    )

# Initialize Gemini model
@st.cache_resource
def initialize_model():
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    system_prompt = """
        You are a helpful assistant specialized in banking document verification.
        Analyze the uploaded PDF files and extract relevant anomalies or issues.
        Provide a short summary, and a bullet list with line numbers.
    """
    return model.start_chat(history=[{"role": "user", "parts": [system_prompt]}])

# PDF display function
def display_pdf(uploaded_file):
    """
    Displays PDF within the UI page.
    """
    base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="680" height="958" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Load model in session
if "chat" not in st.session_state:
    st.session_state.chat = initialize_model()

# Metadata table
case_data = []
for f in uploaded_files:
    case_data.append({
        "Case": f.name,
        "Type": f.type,
        "Client Name": "Amanda Johnson",
        "Client Importance": 5,
        "Urgency": 3,
        "Priority": 4
    })

if case_data:
    df = pd.DataFrame(case_data)
    st.markdown("### Uploaded Cases")
    st.dataframe(df, use_container_width=True)

# File preview and download
if uploaded_files:
    file_names = [f.name for f in uploaded_files]
    selected_file_name = st.selectbox("Choose a case to view", options=file_names)
    selected_file = next(f for f in uploaded_files if f.name == selected_file_name)

    st.download_button("Download PDF", selected_file.getvalue(), file_name=selected_file.name)
    st.markdown("### Preview Document")
    display_pdf(selected_file)

# Chat interface
avatars = {
    "assistant": "images/gemini_avatar.png",
    "user": "images/user_avatar.png"
}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatars.get(msg["role"], None)):
        st.write(msg["content"])

def run_query(input_text):
    try:
        response = st.session_state.chat.send_message(input_text)
        return response.text if response else "Error"
    except Exception:
        return "Error"

if prompt := st.chat_input("Enter your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=avatars["user"]):
        st.write(prompt)

    with st.chat_message("assistant", avatar=avatars["assistant"]):
        with st.spinner("Thinking..."):
            response = run_query(prompt)
            st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
