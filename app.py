import streamlit as st
from typing import List, Any

from src.config import Config
from src.services.ai_processor import AIProcessor
from src.services.chat_service import ChatService
from src.utils.document_parser import DocumentParser
from src.utils.translator import GeminiTranslator

doc_parser = DocumentParser()
ai_processor = AIProcessor()
chat_service = ChatService()
gemini_translator = GeminiTranslator()

SUPPORTED_LANGUAGES = Config.SUPPORTED_LANGUAGES

st.set_page_config(
    page_title="Generative AI for Demystifying Healthcare Documents",
    page_icon=":healthcare:",
    layout="wide"
)

st.markdown("""<style>
/* Global styles */
html, body, .main, .block-container {
    background-color: #1A1A2E;
    color: #E0E0F0;
    font-family: 'Inter', sans-serif;
    line-height: 1.4; /* Further reduced line height */
    scroll-behavior: smooth;
}
p { margin-bottom: 0.4em; } /* Further reduced default paragraph margin */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF;
    font-weight: 700;
    margin-top: 0.8em; /* Further reduced margin-top for headers */
    margin-bottom: 0.3em; /* Further reduced margin-bottom for headers */
    letter-spacing: 0.5px;
}
strong { color: #FFFFFF; }

[data-testid="stSidebar"] {
    display: none;
}

/* File Uploader styling */
div[data-testid="stFileUploader"] {
    border: 2px dashed #00B4D8;
    border-radius: 10px; /* Slightly less rounded */
    background: #2A2A47;
    padding: 12px; /* Further reduced padding */
    margin-top: 12px; /* Further reduced margin-top */
    margin-bottom: 0.2em; /* Aggressively reduced margin-bottom */
    min-height: 130px; /* Smaller height */
}
div[data-testid="stFileUploader"]:hover {
    border-color: #6A05AD;
    background: #303050;
    box-shadow: 0 0 8px rgba(0, 180, 216, 0.2); /* Reduced shadow */
}
.stFileUploader label {
    font-size: 0.9em; /* Smaller font size */
    margin-bottom: 6px; /* Reduced margin-bottom */
}
div[data-testid="stFileUploader"] .st-emotion-cache-1wmy9hp p { /* "Drag and drop" text */
    font-size: 0.9em;
    margin-bottom: 0;
}
div[data-testid="stFileUploader"] .st-emotion-cache-1wmy9hp > div:last-of-type { /* "Limit..." text */
    font-size: 0.75em; /* Even smaller font size */
    margin-top: 1px; /* Reduced margin-top */
}

.stFileUploader button {
    padding: 5px 15px !important; /* Further reduced padding */
    margin-top: 6px; /* Further reduced margin-top */
    font-size: 0.85em; /* Smaller font size */
}
.stFileUploader button:hover {
    transform: translateY(-1px);
    box-shadow: 0px 2px 8px rgba(106, 5, 173, 0.25) !important; /* Reduced shadow */
}

/* New CSS for displaying uploaded file items */
div[data-testid="stFileUploadProgress"] {
    padding: 5px 8px; /* Reduced padding */
    margin-top: 6px; /* Reduced margin-top */
    font-size: 0.85em; /* Smaller font size */
}
div[data-testid="stFileUploadProgress"] div:first-child {
    gap: 5px; /* Reduced gap */
    font-size: 0.85em;
}
div[data-testid="stFileUploadProgress"] svg {
    font-size: 0.9em;
}
button[data-testid="stFileUploaderClearButton"] {
    width: 22px !important; /* Smaller size */
    height: 22px !important;
    font-size: 0.9em !important;
}


/* Header styling */
.app-header {
    padding: 20px; /* Adjusted padding for the box */
    font-size: 32px; /* Made font size bigger */
    margin-bottom: 30px; /* Increased margin-bottom */
    gap: 10px; /* Adjusted gap */
    text-align: center;
    background-color: #2A2A47; /* Added background for the box */
    border: 2px solid #00B4D8; /* Added border for the box */
    border-radius: 15px; /* Added border-radius for rounded corners */
    max-width: 800px; /* Constrain width for a box effect */
    margin-left: auto; /* Center the box */
    margin-right: auto; /* Center the box */
    display: flex; /* Use flex to align icon and text */
    align-items: center; /* Center items vertically */
    justify-content: center; /* Center items horizontally */
}
.app-header svg {
    font-size: 34px; /* Adjusted icon size to match new font size */
    margin-right: 10px; /* Space between icon and text */
}

/* Button styling */
.stButton>button {
    padding: 0.6em 1.3em; /* Reduced padding */
    font-size: 0.9em; /* Smaller font size */
    margin-top: 6px; /* Reduced margin-top */
    margin-bottom: 6px; /* Reduced margin-bottom */
}
.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0px 3px 10px rgba(106, 5, 173, 0.3);
}

/* Chat bubble styling */
.chat-bubble-user, .chat-bubble-ai {
    padding: 10px 15px; /* Reduced padding */
    border-radius: 18px 18px 7px 18px; /* Smaller radius */
    margin: 6px 0; /* Reduced margin */
    font-size: 0.9em; /* Smaller font size */
}
.chat-bubble-ai {
    border-radius: 18px 18px 18px 7px; /* Smaller radius */
}

/* Tabs styling */
.stTabs [data-testid="stTabContent"] {
    padding: 1rem 0; /* Further reduced padding */
}
.stTabs [data-testid="stTab"] {
    margin-right: 6px; /* Reduced margin-right */
    padding: 10px 20px; /* Reduced padding */
    font-size: 1em; /* Smaller font size */
}
.stTabs [data-testid="stTab"][aria-selected="true"] {
    box-shadow: 0px -2px 8px rgba(0, 180, 216, 0.25); /* Reduced shadow */
}

/* Input Fields (Selectbox, Text Input) styling */
div[data-testid="stSelectbox"] > label,
div[data-testid="stTextInput"] label {
    margin-bottom: 4px; /* Reduced margin-bottom */
    font-size: 0.9em; /* Smaller font size */
}

div[data-testid="stSelectbox"] div.st-emotion-cache-1wv8cff,
div[data-testid="stSelectbox"] div.st-emotion-cache-1wv8cff > div {
    padding: 0.4em 0.8em; /* Reduced padding */
}
div[data-testid="stTextInput"] div.st-emotion-cache-1c7y2k2,
div[data-testid="stTextInput"] div.st-emotion-cache-h5rpjc {
    padding: 0.4em 0.8em; /* Reduced padding */
}
div[data-testid="stTextInput"] textarea,
div[data-testid="stTextInput"] input {
    font-size: 0.9em; /* Smaller font size */
}

/* Status messages (success, info, warning, error) */
.stAlert {
    padding: 10px 15px; /* Reduced padding */
    margin-bottom: 10px; /* Reduced margin-bottom */
    font-size: 0.9em; /* Smaller font size */
}

/* Spinner styling */
.stSpinner > div > div {
    font-size: 0.9em; /* Smaller font size */
}

/* Code block styling */
div.stCodeBlock {
    padding: 10px; /* Reduced padding */
    margin-top: 10px; /* Reduced margin-top */
    margin-bottom: 10px; /* Reduced margin-bottom */
    font-size: 0.8em; /* Smaller font size */
}

/* Footer (for copyright) */
.footer {
    padding: 18px 20px; /* Reduced padding */
    font-size: 11px; /* Smaller font size */
    margin-top: 30px; /* Reduced margin-top */
    text-align: center;
    background-color: #2A2A47; /* Added background for the box */
    border: 1px solid #00B4D8; /* Added border for the box */
    border-radius: 8px; /* Added border-radius for rounded corners */
    /* Ensure it covers full width relative to its Streamlit container */
    margin-left: -20px; /* Adjust to extend to the edge of the Streamlit block container if needed */
    margin-right: -20px; /* Adjust to extend to the edge of the Streamlit block container if needed */
    width: calc(100% + 40px); /* Fill the width of the main content area */
    position: relative; /* Needed for negative margins to work correctly */
    box-sizing: border-box; /* Include padding and border in the element's total width and height */
}


/* Streamlit container padding/gap overrides */
.st-emotion-cache-nahz7x {
    padding-top: 0.2rem;
    padding-bottom: 0.2rem;
}
.st-emotion-cache-czk5ad.ezrtsby2 {
    gap: 0.2rem;
}
.st-emotion-cache-ocqkz7 {
    padding-top: 0.2rem;
    padding-bottom: 0.2rem;
}
.st-emotion-cache-1jm61g7 {
    margin-bottom: 0.2rem;
}
/* Specific targeting for initial upload screen headings to reduce default block margins */
h2[data-testid="stMarkdownContainer"]:nth-of-type(1) { /* "Get Started" */
    margin-bottom: 0.4em !important;
}
h3[data-testid="stMarkdownContainer"]:nth-of-type(1) { /* "Upload Healthcare Document(s)" */
    margin-bottom: 0.1em !important;
}
h3[data-testid="stMarkdownContainer"]:nth-of-type(2) { /* "Answer Language" */
    margin-top: 0.4em !important;
    margin-bottom: 0.1em !important;
}

</style>""", unsafe_allow_html=True)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'action_outputs' not in st.session_state:
    st.session_state.action_outputs = {}

if 'document_processed' not in st.session_state:
    st.session_state.document_processed = False
if 'document_text' not in st.session_state:
    st.session_state.document_text = None
if 'doc_type' not in st.session_state:
    st.session_state.doc_type = "Unknown"
if 'lang' not in st.session_state: 
    st.session_state.lang = "English"

def reset_app_state():
    st.session_state.document_processed = False
    st.session_state.document_text = None
    st.session_state.doc_type = "Unknown"
    st.session_state.chat_history = []
    st.session_state.action_outputs = {}
    st.session_state.uploaded_files_key = st.session_state.get('uploaded_files_key', 0) + 1

st.markdown('<div class="app-header">Generative AI for Demystifying Healthcare Documents</div>', unsafe_allow_html=True)

if not st.session_state.document_processed:
    st.markdown("<h2 style='text-align: center; color: #E0E0F0; margin-bottom: 0.3em;'>Get Started: Upload Your Healthcare Document(s)</h2>", unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 3, 1])

    with center_col:
        st.markdown("### <div style='text-align: center; margin-bottom: 0.1em;'>Upload Healthcare Document(s)</div>", unsafe_allow_html=True)

        if 'uploaded_files_key' not in st.session_state:
            st.session_state.uploaded_files_key = 0

        uploaded_files = st.file_uploader(
            "Drag and drop your healthcare document(s) (PDF, JPEG, or PNG) here",
            type=["pdf", "jpg", "jpeg", "png", "txt"],
            accept_multiple_files=True,
            key=f"file_uploader_initial_{st.session_state.uploaded_files_key}",
            label_visibility="collapsed"
        )

        st.markdown("### <div style='text-align: center; margin-top: 0.3em; margin-bottom: 0.1em;'>Answer Language</div>", unsafe_allow_html=True)
        lang_col_left, lang_col_center_inner, lang_col_right = st.columns([0.5, 2, 0.5])
        with lang_col_center_inner:
            st.session_state.lang = st.selectbox(
                "Select Language for AI Responses",
                SUPPORTED_LANGUAGES,
                key="lang_select_initial",
                label_visibility="collapsed",
                index=SUPPORTED_LANGUAGES.index(st.session_state.lang) if st.session_state.lang in SUPPORTED_LANGUAGES else 0
            )

        st.markdown(
            "<p style='text-align: center; margin-top: 0.5em; color: #A0A0B5; font-size: 0.9em;'>"
                "Upload <strong>one or more</strong> healthcare documents (insurance policies, medical reports, prescriptions) in PDF, JPEG, PNG, or TXT format above. "
            "Our AI will extract and <strong>combine their content for comprehensive analysis</strong> and interaction."
            "</p>", unsafe_allow_html=True
        )

    if uploaded_files:
        current_file_ids = [f.file_id if hasattr(f, 'file_id') else f.name for f in uploaded_files]
        if 'last_processed_file_ids' not in st.session_state or st.session_state.last_processed_file_ids != current_file_ids:
            st.session_state.last_processed_file_ids = current_file_ids

            num_files = len(uploaded_files)
            if num_files == 1:
                st.success("1 healthcare document uploaded successfully! Processing...")
            else:
                st.success(f"{num_files} healthcare documents uploaded successfully! Text extraction initiated...")

            all_extracted_texts = []
            processing_errors = []

            for uploaded_file in uploaded_files:
                try:
                    is_file_valid, file_validation_msg = Config.validate_file(uploaded_file)
                    if not is_file_valid:
                        processing_errors.append(f"File '{uploaded_file.name}' failed validation: {file_validation_msg}")
                        continue

                    with st.spinner(f"Extracting text from '{uploaded_file.name}'..."):
                        extracted_text_single_file = doc_parser.extract_text_from_file(uploaded_file)
                        if extracted_text_single_file and extracted_text_single_file.strip():
                            all_extracted_texts.append(extracted_text_single_file)
                        else:
                            processing_errors.append(f"No readable text found in '{uploaded_file.name}'. This file will not contribute to the combined document.")

                except Exception as e:
                    processing_errors.append(f"Error processing '{uploaded_file.name}': {e}. This file will not contribute to the combined document.")

            document_text = "\n\n".join(all_extracted_texts).strip()

            if processing_errors:
                for error_msg in processing_errors:
                    st.error(f"{error_msg}")

            if document_text:
                processed_text = doc_parser.preprocess_text(document_text)
                is_valid, validation_msg = doc_parser.validate_extracted_text(processed_text)

                if is_valid:
                    with st.spinner("Classifying document type..."):
                        classification_result = ai_processor.classify_document(processed_text)
                        doc_type = classification_result.get("document_type", "Other Legal Document")

                    st.session_state.document_text = processed_text
                    st.session_state.doc_type = doc_type
                    st.session_state.document_processed = True
                    st.session_state.chat_history = []
                    st.session_state.action_outputs = {}
                    st.rerun()
                else:
                    st.error(f"Document content validation failed: {validation_msg}. Please ensure your document contains meaningful legal/healthcare text and try again.")
            else:
                st.error("No meaningful text could be extracted from any of the uploaded documents. Please try again with different files or check file content.")


else:
    document_text = st.session_state.document_text
    doc_type = st.session_state.doc_type

    header_col_left, header_col_lang, header_col_reset = st.columns([2, 1, 1])

    with header_col_lang:
        st.markdown("<span style='color: #E0E0F0; margin-right: 6px; font-weight: 600; font-size: 0.9em; display: block; margin-bottom: 0.5em;'>Language:</span>", unsafe_allow_html=True)
        st.session_state.lang = st.selectbox(
            "Answer Language",
            SUPPORTED_LANGUAGES,
            key="lang_select_persistent",
            label_visibility="collapsed",
            index=SUPPORTED_LANGUAGES.index(st.session_state.lang) if st.session_state.lang in SUPPORTED_LANGUAGES else 0
        )
    with header_col_reset:
        st.markdown("<div style='height: 1.8em;'></div>", unsafe_allow_html=True)
        if st.button("Start Over", on_click=reset_app_state, use_container_width=True, key="btn_new_document"):
            st.info("Application state reset. Please upload a new document to begin again.")

    st.markdown("<div style='border-top: 1px solid #353550; margin-top: 1em; margin-bottom: 1em;'></div>", unsafe_allow_html=True)
    st.subheader("Document Interaction & AI Assistant")

    tab1, tab2, tab3 = st.tabs(["Document View", "Actions", "Ask AI"])

    with tab1:
        st.write(f"**Detected Document Type (overall):** <span style='color:#00B4D8;'>{doc_type}</span>", unsafe_allow_html=True)
        st.markdown("<div style='border-top: 1px solid #353550; margin-top: 0.8em; margin-bottom: 0.8em;'></div>", unsafe_allow_html=True)
        st.info("Below is the **combined extracted text** from all your uploaded document(s). A truncated version is displayed for preview. The full combined text is utilized for all AI processing in the 'Actions' and 'Ask AI' tabs.")
        st.code(document_text[:Config.MAX_DOCUMENT_LENGTH // 5] + "...\n\n[Truncated for preview. Full text is available for processing.]", language="text")

    with tab2:
        st.write(f"**Document Type (overall):** <span style='color:#00B4D8;'>{doc_type}</span>", unsafe_allow_html=True)
        st.markdown("<div style='border-top: 1px solid #353550; margin-top: 0.8em; margin-bottom: 0.8em;'></div>", unsafe_allow_html=True)
        st.write("Perform various AI-powered actions on your uploaded document:")
        st.markdown("<div style='border-top: 1px solid #353550; margin-top: 0.8em; margin-bottom: 0.8em;'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Extract Key Information", use_container_width=True, key="btn_key_info"):
                with st.spinner("Extracting key entities..."):
                    chat_service.set_document_context(document_text, doc_type)
                    result = ai_processor.extract_entities(document_text, doc_type, st.session_state.lang)
                    st.session_state.action_outputs["key_info"] = {"type": "success", "header": "Key Information Extracted Successfully!", "content": result}
                st.rerun()

            if st.button("Risk Assessment", use_container_width=True, key="btn_risk_assessment"):
                with st.spinner("Performing risk assessment..."):
                    chat_service.set_document_context(document_text, doc_type)
                    result = ai_processor.perform_risk_analysis(document_text, doc_type, st.session_state.lang)
                    st.session_state.action_outputs["risk_assessment"] = {"type": "warning", "header": "Risk Assessment Complete:", "content": result}
                st.rerun()

            if st.button("Explain Complex Terms", use_container_width=True, key="btn_explain_terms"):
                with st.spinner("Explaining complex terms..."):
                    chat_service.set_document_context(document_text, doc_type)
                    result = ai_processor.explain_complex_terms(document_text, doc_type, st.session_state.lang)
                    st.session_state.action_outputs["explain_terms"] = {"type": "info", "header": "Complex Terms Explained:", "content": result}
                st.rerun()

        with col2:
            if st.button("Generate Compliance Checklist", use_container_width=True, key="btn_checklist"):
                with st.spinner("Generating compliance checklist..."):
                    chat_service.set_document_context(document_text, doc_type)
                    result = ai_processor.generate_compliance_checklist(document_text, doc_type, st.session_state.lang)
                    st.session_state.action_outputs["compliance_checklist"] = {"type": "success", "header": "Compliance Checklist Generated:", "content": result}
                st.rerun()

            if st.button("Summarize Document", use_container_width=True, key="btn_summarize"):
                with st.spinner("Summarizing document..."):
                    chat_service.set_document_context(document_text, doc_type)
                    result = ai_processor.summarize_document(document_text, doc_type, st.session_state.lang)
                    st.session_state.action_outputs["summarize_document"] = {"type": "success", "header": "Document Summarized:", "content": result}
                st.rerun()

            if st.button("Simplify Document", use_container_width=True, key="btn_simplify"):
                with st.spinner("Simplifying text..."):
                    chat_service.set_document_context(document_text, doc_type)
                    result = ai_processor.simplify_document(document_text, doc_type, st.session_state.lang)
                    st.session_state.action_outputs["simplify_document"] = {"type": "info", "header": "Document Simplified (Plain Language):", "content": result}
                st.rerun()

        if st.session_state.action_outputs:
            st.markdown("<div style='border-top: 1px solid #353550; margin-top: 1em; margin-bottom: 1em;'></div>", unsafe_allow_html=True)
            st.subheader("Results:")
            for key, output in st.session_state.action_outputs.items():
                if output["type"] == "success":
                    st.success(output["header"])
                elif output["type"] == "warning":
                    st.warning(output["header"])
                elif output["type"] == "info":
                    st.info(output["header"])
                st.markdown(output["content"])
                st.markdown("<div style='border-top: 1px dashed #353550; margin-top: 0.8em; margin-bottom: 0.8em;'></div>", unsafe_allow_html=True)
    with tab3:
        st.markdown("<div style='border-top: 1px solid #353550; margin-top: 1em; margin-bottom: 1em;'></div>", unsafe_allow_html=True)
        st.write("Ask questions about your document using our AI Assistant:")
        st.markdown("<div style='border-top: 1px solid #353550; margin-top: 0.8em; margin-bottom: 0.8em;'></div>", unsafe_allow_html=True)

        chat_service.set_document_context(document_text, doc_type)

        for entry in st.session_state.chat_history:
            if entry["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user">{entry["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai">{entry["content"]}</div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
        user_input = st.text_input("Type your question...", key="chat_input", placeholder="e.g., What are the key responsibilities of Party A?")

        col_ask, _ = st.columns([0.2, 0.8])
        with col_ask:
            if st.button("Ask", key="ask_button", use_container_width=True):
                if user_input:
                    st.session_state.chat_history.append({"role": "user", "content": user_input})

                    with st.spinner("Processing your query..."):
                        response = chat_service.ask_question(user_input, language=st.session_state.lang)
                        st.session_state.chat_history.append({"role": "ai", "content": response})
                    st.rerun()
                else:
                    st.warning("Please type a question to ask.")

st.markdown("""
<div class="footer">
    Generative AI for Demystifying Healthcare Documents.
</div>
""", unsafe_allow_html=True)