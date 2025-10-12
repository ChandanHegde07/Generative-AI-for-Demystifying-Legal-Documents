import streamlit as st
from typing import List, Any
from functools import lru_cache

from src.config import Config
from src.services.ai_processor import AIProcessor
from src.services.chat_service import ChatService
from src.utils.document_parser import DocumentParser
from src.utils.translator import GeminiTranslator

@st.cache_resource
def get_doc_parser():
    return DocumentParser()

@st.cache_resource
def get_ai_processor():
    return AIProcessor()

@st.cache_resource
def get_chat_service():
    return ChatService()

@st.cache_resource
def get_gemini_translator():
    return GeminiTranslator()

doc_parser = get_doc_parser()
ai_processor = get_ai_processor()
chat_service = get_chat_service()
gemini_translator = get_gemini_translator()

SUPPORTED_LANGUAGES = Config.SUPPORTED_LANGUAGES

st.set_page_config(
    page_title="Generative AI for Demystifying Healthcare Documents",
    page_icon=":healthcare:",
    layout="wide"
)


@st.cache_data
def get_custom_css():
    return """<style>
/* Global styles */
html, body, .main, .block-container {
    background-color: #1A1A2E;
    color: #E0E0F0;
    font-family: 'Inter', sans-serif;
    line-height: 1.4;
    scroll-behavior: smooth;
}
p { margin-bottom: 0.4em; }
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF;
    font-weight: 700;
    margin-top: 0.8em;
    margin-bottom: 0.3em;
    letter-spacing: 0.5px;
}
strong { color: #FFFFFF; }

[data-testid="stSidebar"] {
    display: none;
}

/* File Uploader styling */
div[data-testid="stFileUploader"] {
    border: 2px dashed #00B4D8;
    border-radius: 10px;
    background: #2A2A47;
    padding: 12px;
    margin-top: 12px;
    margin-bottom: 0.2em;
    min-height: 130px;
}
div[data-testid="stFileUploader"]:hover {
    border-color: #6A05AD;
    background: #303050;
    box-shadow: 0 0 8px rgba(0, 180, 216, 0.2);
}
.stFileUploader label {
    font-size: 0.9em;
    margin-bottom: 6px;
}
div[data-testid="stFileUploader"] .st-emotion-cache-1wmy9hp p {
    font-size: 0.9em;
    margin-bottom: 0;
}
div[data-testid="stFileUploader"] .st-emotion-cache-1wmy9hp > div:last-of-type {
    font-size: 0.75em;
    margin-top: 1px;
}

.stFileUploader button {
    padding: 5px 15px !important;
    margin-top: 6px;
    font-size: 0.85em;
}
.stFileUploader button:hover {
    transform: translateY(-1px);
    box-shadow: 0px 2px 8px rgba(106, 5, 173, 0.25) !important;
}

div[data-testid="stFileUploadProgress"] {
    padding: 5px 8px;
    margin-top: 6px;
    font-size: 0.85em;
}
div[data-testid="stFileUploadProgress"] div:first-child {
    gap: 5px;
    font-size: 0.85em;
}
div[data-testid="stFileUploadProgress"] svg {
    font-size: 0.9em;
}
button[data-testid="stFileUploaderClearButton"] {
    width: 22px !important;
    height: 22px !important;
    font-size: 0.9em !important;
}

/* Header styling */
.app-header {
    padding: 20px;
    font-size: 32px;
    margin-bottom: 30px;
    gap: 10px;
    text-align: center;
    background-color: #2A2A47;
    border: 2px solid #00B4D8;
    border-radius: 15px;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
    display: flex;
    align-items: center;
    justify-content: center;
}
.app-header svg {
    font-size: 34px;
    margin-right: 10px;
}

/* Button styling */
.stButton>button {
    padding: 0.6em 1.3em;
    font-size: 0.9em;
    margin-top: 6px;
    margin-bottom: 6px;
}
.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0px 3px 10px rgba(106, 5, 173, 0.3);
}

/* Chat bubble styling */
.chat-bubble-user, .chat-bubble-ai {
    padding: 10px 15px;
    border-radius: 18px 18px 7px 18px;
    margin: 6px 0;
    font-size: 0.9em;
}
.chat-bubble-ai {
    border-radius: 18px 18px 18px 7px;
}

/* Tabs styling */
.stTabs [data-testid="stTabContent"] {
    padding: 1rem 0;
}
.stTabs [data-testid="stTab"] {
    margin-right: 6px;
    padding: 10px 20px;
    font-size: 1em;
}
.stTabs [data-testid="stTab"][aria-selected="true"] {
    box-shadow: 0px -2px 8px rgba(0, 180, 216, 0.25);
}

/* Input Fields styling */
div[data-testid="stSelectbox"] > label,
div[data-testid="stTextInput"] label {
    margin-bottom: 4px;
    font-size: 0.9em;
}

div[data-testid="stSelectbox"] div.st-emotion-cache-1wv8cff,
div[data-testid="stSelectbox"] div.st-emotion-cache-1wv8cff > div {
    padding: 0.4em 0.8em;
}
div[data-testid="stTextInput"] div.st-emotion-cache-1c7y2k2,
div[data-testid="stTextInput"] div.st-emotion-cache-h5rpjc {
    padding: 0.4em 0.8em;
}
div[data-testid="stTextInput"] textarea,
div[data-testid="stTextInput"] input {
    font-size: 0.9em;
}

/* Status messages */
.stAlert {
    padding: 10px 15px;
    margin-bottom: 10px;
    font-size: 0.9em;
}

/* Spinner styling */
.stSpinner > div > div {
    font-size: 0.9em;
}

/* Code block styling */
div.stCodeBlock {
    padding: 10px;
    margin-top: 10px;
    margin-bottom: 10px;
    font-size: 0.8em;
}

/* Footer */
.footer {
    padding: 18px 20px;
    font-size: 11px;
    margin-top: 30px;
    text-align: center;
    background-color: #2A2A47;
    border: 1px solid #00B4D8;
    border-radius: 8px;
    margin-left: -20px;
    margin-right: -20px;
    width: calc(100% + 40px);
    position: relative;
    box-sizing: border-box;
}

/* Streamlit container overrides */
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
h2[data-testid="stMarkdownContainer"]:nth-of-type(1) {
    margin-bottom: 0.4em !important;
}
h3[data-testid="stMarkdownContainer"]:nth-of-type(1) {
    margin-bottom: 0.1em !important;
}
h3[data-testid="stMarkdownContainer"]:nth-of-type(2) {
    margin-top: 0.4em !important;
    margin-bottom: 0.1em !important;
}
</style>"""

st.markdown(get_custom_css(), unsafe_allow_html=True)

def init_session_state():
    
    defaults = {
        'chat_history': [],
        'action_outputs': {},
        'document_processed': False,
        'document_text': None,
        'doc_type': "Unknown",
        'lang': "English",
        'uploaded_files_key': 0
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

def reset_app_state():
    st.session_state.document_processed = False
    st.session_state.document_text = None
    st.session_state.doc_type = "Unknown"
    st.session_state.chat_history = []
    st.session_state.action_outputs = {}
    st.session_state.uploaded_files_key += 1

@st.cache_data
def render_header():
    return '<div class="app-header">Generative AI for Demystifying Healthcare Documents</div>'

st.markdown(render_header(), unsafe_allow_html=True)

if not st.session_state.document_processed:
    st.markdown("<h2 style='text-align: center; color: #E0E0F0; margin-bottom: 0.3em;'>Get Started: Upload Your Healthcare Document(s)</h2>", unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 3, 1])

    with center_col:
        st.markdown("### <div style='text-align: center; margin-bottom: 0.1em;'>Upload Healthcare Document(s)</div>", unsafe_allow_html=True)

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
            
            ai_processor.reset_pii_mapping()
            chat_service.reset_pii_mapping()

            num_files = len(uploaded_files)
            status_msg = "1 healthcare document uploaded successfully! Processing..." if num_files == 1 else f"{num_files} healthcare documents uploaded successfully! Text extraction initiated..."
            st.success(status_msg)

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
                            processing_errors.append(f"No readable text found in '{uploaded_file.name}'.")

                except Exception as e:
                    processing_errors.append(f"Error processing '{uploaded_file.name}': {e}")

            document_text = "\n\n".join(all_extracted_texts).strip()

            for error_msg in processing_errors:
                st.error(error_msg)

            if document_text:
                processed_text = doc_parser.preprocess_text(document_text)
                is_valid, validation_msg = doc_parser.validate_extracted_text(processed_text)

                if is_valid:
                    with st.spinner("Classifying document type..."):
                        classification_result = ai_processor.classify_document(processed_text)
                        doc_type = classification_result.get("document_type", "Other Legal Document")

                    st.session_state.update({
                        'document_text': processed_text,
                        'doc_type': doc_type,
                        'document_processed': True,
                        'chat_history': [],
                        'action_outputs': {}
                    })
                    st.rerun()
                else:
                    st.error(f"Document content validation failed: {validation_msg}")
            else:
                st.error("No meaningful text could be extracted from any of the uploaded documents.")

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
            st.rerun()

    st.markdown("<div style='border-top: 1px solid #353550; margin-top: 1em; margin-bottom: 1em;'></div>", unsafe_allow_html=True)
    st.subheader("Document Interaction & AI Assistant")

    tab1, tab2, tab3 = st.tabs(["Document View", "Actions", "Ask AI"])

    with tab1:
        st.write(f"**Detected Document Type (overall):** <span style='color:#00B4D8;'>{doc_type}</span>", unsafe_allow_html=True)
        st.markdown("<div style='border-top: 1px solid #353550; margin-top: 0.8em; margin-bottom: 0.8em;'></div>", unsafe_allow_html=True)
        st.info("Below is the **combined extracted text** from all your uploaded document(s). A truncated version is displayed for preview.")
        st.code(document_text[:Config.MAX_DOCUMENT_LENGTH // 5] + "...\n\n[Truncated for preview. Full text is available for processing.]", language="text")

    with tab2:
        st.write(f"**Document Type (overall):** <span style='color:#00B4D8;'>{doc_type}</span>", unsafe_allow_html=True)
        st.markdown("<div style='border-top: 1px solid #353550; margin-top: 0.8em; margin-bottom: 0.8em;'></div>", unsafe_allow_html=True)
        st.write("Perform various AI-powered actions on your uploaded document:")
        st.markdown("<div style='border-top: 1px solid #353550; margin-top: 0.8em; margin-bottom: 0.8em;'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        def handle_action(action_key, spinner_text, method, output_type, header_text):
            with st.spinner(spinner_text):
                chat_service.set_document_context(document_text, doc_type)
                result = method(document_text, doc_type, st.session_state.lang)
                st.session_state.action_outputs[action_key] = {
                    "type": output_type, 
                    "header": header_text, 
                    "content": result
                }
            st.rerun()

        with col1:
            if st.button("Extract Key Information", use_container_width=True, key="btn_key_info"):
                handle_action("key_info", "Extracting key entities...", 
                            ai_processor.extract_entities, "success", 
                            "Key Information Extracted Successfully!")

            if st.button("Risk Assessment", use_container_width=True, key="btn_risk_assessment"):
                handle_action("risk_assessment", "Performing risk assessment...", 
                            ai_processor.perform_risk_analysis, "warning", 
                            "Risk Assessment Complete:")

            if st.button("Explain Complex Terms", use_container_width=True, key="btn_explain_terms"):
                handle_action("explain_terms", "Explaining complex terms...", 
                            ai_processor.explain_complex_terms, "info", 
                            "Complex Terms Explained:")

        with col2:
            if st.button("Generate Compliance Checklist", use_container_width=True, key="btn_checklist"):
                handle_action("compliance_checklist", "Generating compliance checklist...", 
                            ai_processor.generate_compliance_checklist, "success", 
                            "Compliance Checklist Generated:")

            if st.button("Summarize Document", use_container_width=True, key="btn_summarize"):
                handle_action("summarize_document", "Summarizing document...", 
                            ai_processor.summarize_document, "success", 
                            "Document Summarized:")

            if st.button("Simplify Document", use_container_width=True, key="btn_simplify"):
                handle_action("simplify_document", "Simplifying text...", 
                            ai_processor.simplify_document, "info", 
                            "Document Simplified (Plain Language):")

        if st.session_state.action_outputs:
            st.markdown("<div style='border-top: 1px solid #353550; margin-top: 1em; margin-bottom: 1em;'></div>", unsafe_allow_html=True)
            st.subheader("Results:")
            
            for key, output in st.session_state.action_outputs.items():
                msg_func = {"success": st.success, "warning": st.warning, "info": st.info}[output["type"]]
                msg_func(output["header"])
                st.markdown(output["content"])
                st.markdown("<div style='border-top: 1px dashed #353550; margin-top: 0.8em; margin-bottom: 0.8em;'></div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div style='border-top: 1px solid #353550; margin-top: 1em; margin-bottom: 1em;'></div>", unsafe_allow_html=True)
        st.write("Ask questions about your document using our AI Assistant:")
        st.markdown("<div style='border-top: 1px solid #353550; margin-top: 0.8em; margin-bottom: 0.8em;'></div>", unsafe_allow_html=True)

        chat_service.set_document_context(document_text, doc_type)

        for entry in st.session_state.chat_history:
            bubble_class = "chat-bubble-user" if entry["role"] == "user" else "chat-bubble-ai"
            st.markdown(f'<div class="{bubble_class}">{entry["content"]}</div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
        user_input = st.text_input("Type your question...", key="chat_input", 
                                   placeholder="e.g., What are the key responsibilities of Party A?")

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

@st.cache_data
def render_footer():
    return """
<div class="footer">
    Generative AI for Demystifying Healthcare Documents.
</div>
"""

st.markdown(render_footer(), unsafe_allow_html=True)