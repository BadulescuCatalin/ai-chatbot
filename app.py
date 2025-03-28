
import streamlit as st
from qdrant_api import insert_text_chunks, query_similar_texts
from io import StringIO
from dotenv import load_dotenv
import google.generativeai as genai
import os
import base64
from chunking import semantic_chunking, read_pdf_text

st.set_page_config(page_title='FraudSniff', 
                    page_icon = "images/gemini_avatar.png",
                    initial_sidebar_state = 'auto')


@st.cache_data
def initialize_model():
    """
    Configure the Google generativeai with the GEMINI_API_KEY
    """
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    system_prompt = """
        #INSTRUNCTIONS
        You are a helpful assistant specialized in computational chemistry. 
        If a SMILES string is given, respond with the common and IUPAC name of the compound.

        #OUTPUT
        Format allways the outpus as a JSON, with the following fields:
        - SMILES string
        - Name of the compound
        - IUPAC Name
    """
    chat = model.start_chat(
            history=[{
                        "role": "user",
                        "parts": [system_prompt]
                    }]
            )
    return chat


if "chat" not in st.session_state:
    st.session_state.chat = initialize_model()


background_color = "#252740"

avatars = {
    "assistant" : "images/logo.png",
    "user": "images/user_avatar.png"
}

st.markdown("<h2 style='text-align: center; color: #3184a0;'>Document Fraud Detection Chatbot</h2>", unsafe_allow_html=True)
# st.markdown("<h4 style='text-align: center; color: #3184a0;'>Enter the SMILES Code to return the IUPAC name and the name of the compound</h4>", unsafe_allow_html=True)

def display_pdf(uploaded_file):
    """
    Displays PDF within the UI page.
    """
    base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="680" height="958" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)


with st.sidebar:
    st.image("images/logo.png",  width=200)

    # Document type dropdown
    st.markdown("---")
    st.markdown("### 📑 Document Type")
    doc_type = st.selectbox(
    "Choose the type of document",
    ["Select...", "Contract", "Terms and Conditions"])
    
    # File upload
    st.markdown("---")
    st.markdown("### 📤 Upload PDF")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf"])
    
    # === Extract text from PDF ===
    text = read_pdf_text(uploaded_file)

    # === Chunk the text ===
    chunks = semantic_chunking(text)
    doc_id = "doc1"
    inserted = insert_text_chunks(doc_id, chunks)
    results = query_similar_texts("Duties", threshold=0.2)
    print(f"Results {results} chunks.")
    print(f"Inserted {inserted} chunks.")
    st.write(results)
    # # === Print the chunks ===
    # print("\n--- Chunks ---\n")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1}:\n{chunk}\n{'-' * 40}")
    # if uploaded_file is not None:
    #     display_pdf(uploaded_file)

    # Show extra checkboxes based on selected document type
    if doc_type == "Contract":
        st.markdown("---")
        st.markdown("### ✍️ Contract Checks")
        check_fees = st.checkbox("🔍 Check for hidden fees")
        check_unfair = st.checkbox("⛔ Detect unfair clauses")
        check_autorenew = st.checkbox("🔁 Identify auto-renewal traps")

    elif doc_type == "Terms and Conditions":
        st.markdown("---")
        st.markdown("### 📋 T&C Checks")
        check_data_sharing = st.checkbox("🕵️ Track data sharing practices")
        check_user_lockin = st.checkbox("⛓️ Look for user-lock-in policies")
        check_vague_terms = st.checkbox("⚠️ Highlight vague responsibilities")
        
    # Big scan button
    st.markdown("<br>", unsafe_allow_html=True)
    scan_clicked = st.button("🚀 Scan My Document", use_container_width=True)
    
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"], 
                         avatar=avatars[message["role"]]):
        st.write(message["content"])

if uploaded_file is not None:
    st.markdown("<h4 style='color: #3184a0;'>Document Preview</h4>", unsafe_allow_html=True)
    display_pdf(uploaded_file)

def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}
    ]
    
st.sidebar.button("Clear Chat History", on_click=clear_chat_history)

def run_query(input_text):
    """
    Run query. The model is initialized and then queried.
    Args:
        input_text (str): we are just passing to the model the user prompt
    Returns:
        response.text (str): the text of the response
    """
    try:
        
        response = st.session_state.chat.send_message(input_text)

        if response:
            return response.text
        
        else:
            return "Error"

    except Exception as ex:
        return "Error"
    

output = st.empty()
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=avatars["user"]):
        st.write(prompt)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar=avatars["assistant"]):
        with st.spinner("Thinking..."):
            

            response = run_query(prompt)

            placeholder = st.empty()
            full_response = ""
            for item in response:
                full_response += item
                placeholder.markdown(full_response, unsafe_allow_html=True)
            placeholder.markdown(response, unsafe_allow_html=True)

    message = {"role": "assistant", 
               "content": response,
               "avatar": avatars["assistant"]}
    st.session_state.messages.append(message)