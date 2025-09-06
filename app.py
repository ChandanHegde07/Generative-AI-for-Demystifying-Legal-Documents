import streamlit as st
from main import extract_text_from_pdfs, ask_gemini, simplify_text, summarize_text, translate_text

st.set_page_config(page_title="Legal Document AI Assistant", page_icon="⚖️", layout="wide")

st.title("Generative AI for Demystifying Legal Documents")
st.markdown("Upload one or more legal/medical PDFs or scanned documents. The assistant extracts text, simplifies complex terms, translates into regional languages, and lets you ask questions interactively.")

# Sidebar
with st.sidebar:
    st.header("Upload & Settings")
    uploaded_files = st.file_uploader(
        "Upload one or more PDFs", type=["pdf"], accept_multiple_files=True
    )

    st.subheader("Language")
    language = st.selectbox(
        "Answer language:",
        ["English", "Hindi", "Kannada", "French", "German", "Spanish", "Tamil", "Telugu"],
        index=0
    )

    if st.button("Clear Chat", type="primary", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.pdf_text = ""
        st.rerun()

# Initialize session state
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Document Input + OCR
if uploaded_files and not st.session_state.pdf_text:
    with st.spinner("Extracting text from documents..."):
        st.session_state.pdf_text = extract_text_from_pdfs(uploaded_files)
    st.success("Text extracted from all documents!")

# Preview
if st.session_state.pdf_text:
    with st.expander("Preview Extracted Text", expanded=False):
        st.text_area("Extracted Text", st.session_state.pdf_text[:2000], height=300)

    # AI Simplification
    if st.button("✨ Simplify Document(s)"):
        with st.spinner("Simplifying content..."):
            simplified = simplify_text(st.session_state.pdf_text)
            st.session_state.chat_history.append(("Simplified Summary", simplified))
        st.success("Document(s) simplified!")

    # Generate Summary
    if st.button("Generate Summary"):
        with st.spinner("Summarizing content..."):
            summary = summarize_text(st.session_state.pdf_text)
            if language != "English":
                summary = translate_text(summary, language)
            st.session_state.chat_history.append(("Summary", summary))
        st.success("Summary generated!")

# Q&A Section
st.subheader("Ask Your Questions")
with st.form("qa_form", clear_on_submit=True):
    user_question = st.text_input("Enter your question about the document(s):")
    submitted = st.form_submit_button("Get Answer ⚡")

if submitted:
    if not uploaded_files:
        st.warning("Please upload at least one document first.")
    elif not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            answer = ask_gemini(user_question, st.session_state.pdf_text, language)
        st.session_state.chat_history.append((user_question, answer))

# Conversation Display
if st.session_state.chat_history:
    st.markdown("### Conversation")
    for i, (q, a) in enumerate(st.session_state.chat_history, 1):
        st.markdown(f"**Q{i}:** {q}")
        st.markdown(f"**A{i} ({language}):** {a}")
        st.divider()