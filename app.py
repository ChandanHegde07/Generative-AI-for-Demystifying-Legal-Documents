import streamlit as st
import pandas as pd
import re
from main import (
    extract_text_from_files, ask_gemini, summarize_text,
    translate_text, detect_document_type, extract_key_entities,
    generate_compliance_checklist, explain_complex_terms, risk_assessment
)

# ----------------- Helper -----------------
def render_card(text, bg="#fff3cd", border="#ff9800"):
    """Render styled card with proper bold formatting."""
    # Convert Markdown bold (**text**) to HTML <b>text</b>
    safe_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

    st.markdown(f"""
    <div style="background:{bg}; padding:1rem;
                border-left:6px solid {border};
                border-radius:6px; margin:1rem 0; color:#333;">
        {safe_text}
    </div>
    """, unsafe_allow_html=True)

# ----------------- Page Config -----------------
st.set_page_config(
    page_title="Healthcare Document AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ----------------- Sidebar -----------------
with st.sidebar:
    st.header("📂 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDFs or Images",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=True
    )
    language = st.selectbox("Response Language", ["English", "Hindi", "Kannada"], index=0)
    if st.button("🧹 Clear Session", use_container_width=True):
        for key in ["pdf_text", "doc_type", "chat_history"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ----------------- Session State -----------------
for key in ["pdf_text", "doc_type", "chat_history"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "chat_history" else ""

# ----------------- Header -----------------
st.title("🏥 AI-Powered Healthcare Document Assistant")
st.caption("Simplify • Translate • Analyze • Ask Questions")

# ----------------- Processing -----------------
if uploaded_files and not st.session_state.pdf_text:
    with st.spinner("🔄 Processing documents..."):
        text = extract_text_from_files(uploaded_files)
        st.session_state.pdf_text = text
        st.session_state.doc_type = detect_document_type(text)
    st.success("✅ Document processed successfully!")

if not uploaded_files:
    st.info("👆 Upload healthcare documents to begin analysis.")
else:
    st.subheader(f"📋 Detected Document Type: {st.session_state.doc_type}")

    # ----------------- Main Tabs -----------------
    tabs = st.tabs(["🔑 Key Info", "📝 Checklist", "⚠️ Risks", "📄 Summary", "📖 Terms", "💬 Q&A"])

    # --- Key Info Tab ---
    with tabs[0]:
        st.subheader("Key Information")
        key_info = extract_key_entities(st.session_state.pdf_text, st.session_state.doc_type)
        if language != "English":
            key_info = translate_text(key_info, language)
        rows = [line.split(":", 1) for line in key_info.split("\n") if ":" in line]

        if rows:
            df = pd.DataFrame(rows, columns=["Category", "Details"])
            st.table(df)
        else:
            render_card(key_info, bg="#e8f4ff", border="#007bff")

    # --- Checklist Tab ---
    with tabs[1]:
        st.subheader("Action Checklist")
        checklist = generate_compliance_checklist(st.session_state.pdf_text, st.session_state.doc_type)
        if language != "English":
            checklist = translate_text(checklist, language)
        for line in checklist.split("\n"):
            if line.strip().startswith("- [ ]"):
                st.checkbox(line.replace("- [ ]", "").strip(), key=line)
            elif line.strip():
                render_card(line, bg="#f8f9fa", border="#6c757d")

    # --- Risks Tab ---
    with tabs[2]:
        st.subheader("Risk Assessment")
        risks = risk_assessment(st.session_state.pdf_text, st.session_state.doc_type)
        if language != "English":
            risks = translate_text(risks, language)

        # Split into sections by double newline
        sections = [s.strip() for s in risks.split("\n\n") if s.strip()]
        for sec in sections:
            render_card(sec, bg="#fff3cd", border="#ff9800")

    # --- Summary Tab ---
    with tabs[3]:
        st.subheader("Document Summary")
        summary = summarize_text(st.session_state.pdf_text, st.session_state.doc_type)
        if language != "English":
            summary = translate_text(summary, language)
        render_card(summary, bg="#e2f7e1", border="#28a745")

    # --- Terms Tab ---
    with tabs[4]:
        st.subheader("Complex Terms Explained")
        terms = explain_complex_terms(st.session_state.pdf_text, st.session_state.doc_type)
        if language != "English":
            terms = translate_text(terms, language)

        sections = [s.strip() for s in terms.split("\n") if s.strip()]
        for sec in sections:
            render_card(sec, bg="#f1f3f4", border="#6c757d")

    # --- Q&A Tab ---
    with tabs[5]:
        st.subheader("Ask Questions")
        with st.form("qa_form", clear_on_submit=True):
            user_q = st.text_input("Your question:")
            submitted = st.form_submit_button("Get Answer")
        if submitted and user_q.strip():
            answer = ask_gemini(user_q, st.session_state.pdf_text, language, st.session_state.doc_type)
            st.session_state.chat_history.append((user_q, answer))

        # Show conversation history
        if st.session_state.chat_history:
            for q, a in reversed(st.session_state.chat_history):
                render_card(f"<b>Q:</b> {q}<br><b>A:</b> {a}", bg="#f8f9fa", border="#343a40")
