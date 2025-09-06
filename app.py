# app.py
import streamlit as st
from main import extract_text_from_pdf, ask_gemini

st.set_page_config(page_title="Legal Document AI Assistant", page_icon="⚖️", layout="wide")

st.title("⚖️ Generative AI for Demystifying Legal Documents")
st.markdown("Upload a legal PDF, then ask natural language questions about it in your preferred language.")

# Sidebar
with st.sidebar:
    st.header("📂 Upload & Settings")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

    st.subheader("🌍 Language")
    language = st.selectbox(
        "Answer language:",
        ["English", "Hindi", "Kannada", "French", "German", "Spanish", "Tamil", "Telugu"],
        index=0
    )

# Initialize session state
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "clear_trigger" not in st.session_state:
    st.session_state.clear_trigger = False

# PDF Processing
if uploaded_pdf and not st.session_state.pdf_text:
    with st.spinner("Extracting text from PDF..."):
        st.session_state.pdf_text = extract_text_from_pdf(uploaded_pdf)
    st.success("✅ PDF text extracted!")

if st.session_state.pdf_text:
    with st.expander("📄 Preview Extracted Text", expanded=False):
        st.text_area("Extracted Text", st.session_state.pdf_text[:2000], height=300)

# Q&A Form
st.subheader("🔍 Ask Your Questions")
with st.form("qa_form", clear_on_submit=True):
    user_question = st.text_input("Enter your question about the document:")
    submitted = st.form_submit_button("Get Answer ⚡")

if submitted:
    if not uploaded_pdf:
        st.warning("Please upload a PDF first.")
    elif not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            answer = ask_gemini(user_question, st.session_state.pdf_text, language)
        st.session_state.chat_history.append((user_question, answer))

# Conversation Section
if st.session_state.chat_history:
    st.markdown("### 🗨️ Conversation")
    for i, (q, a) in enumerate(st.session_state.chat_history, 1):
        st.markdown(f"**Q{i}:** {q}")
        st.markdown(f"**A{i} ({language}):** {a}")
        st.divider()

    # Clear chat button (instant action)
    if st.button("🧹 Clear Chat", type="primary"):
        st.session_state.chat_history.clear()
        st.success("Chat cleared successfully!")
        st.rerun()  # 👈 force rerun to reflect cleared state immediately