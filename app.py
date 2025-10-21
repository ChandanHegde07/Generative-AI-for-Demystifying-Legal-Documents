import streamlit as st
from typing import List, Any, Dict
from functools import lru_cache
import hashlib

from src.config import Config
from src.services.ai_processor import AIProcessor
from src.services.chat_service import ChatService
from src.services.rag_service import RAGService
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
    page_icon="🔰",
    layout="wide"
)

@st.cache_data
def get_custom_css():

    return """<style>
html,body,.main,.block-container{background-color:#1A1A2E;color:#E0E0F0;font-family:'Inter',sans-serif;line-height:1.4;scroll-behavior:smooth}
p{margin-bottom:.4em}
h1,h2,h3,h4,h5,h6{color:#fff;font-weight:700;margin-top:.8em;margin-bottom:.3em;letter-spacing:.5px}
strong{color:#fff}
[data-testid=stSidebar]{display:none}
div[data-testid=stFileUploader]{border:2px dashed #00B4D8;border-radius:10px;background:#2A2A47;padding:12px;margin-top:12px;margin-bottom:.2em;min-height:130px}
div[data-testid=stFileUploader]:hover{border-color:#6A05AD;background:#303050;box-shadow:0 0 8px rgba(0,180,216,.2)}
.stFileUploader label{font-size:.9em;margin-bottom:6px}
div[data-testid=stFileUploader] .st-emotion-cache-1wmy9hp p{font-size:.9em;margin-bottom:0}
div[data-testid=stFileUploader] .st-emotion-cache-1wmy9hp>div:last-of-type{font-size:.75em;margin-top:1px}
.stFileUploader button{padding:5px 15px!important;margin-top:6px;font-size:.85em}
.stFileUploader button:hover{transform:translateY(-1px);box-shadow:0 2px 8px rgba(106,5,173,.25)!important}
div[data-testid=stFileUploadProgress]{padding:5px 8px;margin-top:6px;font-size:.85em}
div[data-testid=stFileUploadProgress] div:first-child{gap:5px;font-size:.85em}
div[data-testid=stFileUploadProgress] svg{font-size:.9em}
button[data-testid=stFileUploaderClearButton]{width:22px!important;height:22px!important;font-size:.9em!important}
.app-header{padding:20px;font-size:32px;margin-bottom:30px;gap:10px;text-align:center;background-color:#2A2A47;border:2px solid #00B4D8;border-radius:15px;max-width:800px;margin-left:auto;margin-right:auto;display:flex;align-items:center;justify-content:center}
.app-header svg{font-size:34px;margin-right:10px}
.stButton>button{padding:.6em 1.3em;font-size:.9em;margin-top:6px;margin-bottom:6px}
.stButton>button:hover{transform:translateY(-1px);box-shadow:0 3px 10px rgba(106,5,173,.3)}
.stTabs [data-testid=stTabContent]{padding:1rem 0}
.stTabs [data-testid=stTab]{margin-right:6px;padding:10px 20px;font-size:1em}
.stTabs [data-testid=stTab][aria-selected=true]{box-shadow:0 -2px 8px rgba(0,180,216,.25)}
div[data-testid=stSelectbox]>label,div[data-testid=stTextInput] label{margin-bottom:4px;font-size:.9em}
div[data-testid=stSelectbox] div.st-emotion-cache-1wv8cff,div[data-testid=stSelectbox] div.st-emotion-cache-1wv8cff>div{padding:.4em .8em}
div[data-testid=stTextInput] div.st-emotion-cache-1c7y2k2,div[data-testid=stTextInput] div.st-emotion-cache-h5rpjc{padding:.4em .8em}
div[data-testid=stTextInput] textarea,div[data-testid=stTextInput] input{font-size:.9em}
.stAlert{padding:10px 15px;margin-bottom:10px;font-size:.9em}
.stSpinner>div>div{font-size:.9em}
div.stCodeBlock{padding:10px;margin-top:10px;margin-bottom:10px;font-size:.8em}
.footer{padding:18px 20px;font-size:11px;margin-top:30px;text-align:center;background-color:#2A2A47;border:1px solid #00B4D8;border-radius:8px;margin-left:-20px;margin-right:-20px;width:calc(100% + 40px);position:relative;box-sizing:border-box}
</style>"""

st.markdown(get_custom_css(), unsafe_allow_html=True)

def init_session_state():
    defaults = {
        'chat_history': [], 'action_outputs': {}, 'document_processed': False,
        'document_text': None, 'doc_type': "Unknown", 'lang': "English",
        'uploaded_files_key': 0, 'rag_service': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

def reset_app_state():
    current_key = st.session_state.get('uploaded_files_key', 0)
    st.session_state.clear()
    init_session_state()
    st.session_state.uploaded_files_key = current_key + 1

@st.cache_data
def render_header():
    return '<div class="app-header">Generative AI for Demystifying Healthcare Documents</div>'

st.markdown(render_header(), unsafe_allow_html=True)

if not st.session_state.document_processed:
    st.markdown("<h2 style='text-align: center;'>Get Started: Upload Your Document(s)</h2>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 3, 1])
    with center_col:
        st.markdown("#### Upload Healthcare Document(s)", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Upload", type=["pdf", "jpg", "jpeg", "png", "txt"], accept_multiple_files=True, key=f"file_uploader_{st.session_state.uploaded_files_key}", label_visibility="collapsed")
        st.markdown("#### Answer Language", unsafe_allow_html=True)
        _, lang_col, _ = st.columns([0.5, 2, 0.5])
        with lang_col:
            st.session_state.lang = st.selectbox("Language", SUPPORTED_LANGUAGES, key="lang_select_initial", label_visibility="collapsed", index=SUPPORTED_LANGUAGES.index(st.session_state.lang))
        st.markdown("<p style='text-align: center; margin-top: 1em; color: #A0A0B5;'>Upload <strong>one or more</strong> documents. Our AI will combine their content for analysis.</p>", unsafe_allow_html=True)

    if uploaded_files:
        with st.status(f"Processing {len(uploaded_files)} document(s)...", expanded=True) as status:
            all_texts, errors = [], []
            for up_file in uploaded_files:
                st.write(f"Extracting text from `{up_file.name}`...")
                try:
                    is_valid, msg = Config.validate_file(up_file)
                    if not is_valid:
                        errors.append(f"'{up_file.name}' is invalid: {msg}")
                        continue
                    up_file.seek(0)
                    text = doc_parser.extract_text_from_file(up_file)
                    is_valid, msg = doc_parser.validate_extracted_text(text)
                    if not is_valid:
                        errors.append(f"Could not process '{up_file.name}': {msg}")
                    else:
                        all_texts.append(text)
                except Exception as e:
                    errors.append(f"Error with `{up_file.name}`: {e}")
            
            for error in errors: st.error(error)
            
            if all_texts:
                st.write("Analyzing document content...")
                doc_text = doc_parser.preprocess_text("\n\n".join(all_texts))
                classification = ai_processor.classify_document(doc_text)
                doc_type = classification.get("document_type", "Other")
                st.write("Creating searchable index for Q&A...")
                rag_service = RAGService(doc_text)
                st.session_state.update({'document_text': doc_text, 'doc_type': doc_type, 'document_processed': True, 'rag_service': rag_service, 'chat_history': [], 'action_outputs': {}})
                status.update(label="Processing Complete!", state="complete", expanded=False)
                st.rerun()
            else:
                status.update(label="Processing Failed", state="error", expanded=True)
                if not errors: st.error("No meaningful text could be extracted.")

else:
    doc_text, doc_type = st.session_state.document_text, st.session_state.doc_type
    _, lang_col, reset_col = st.columns([2, 1, 1])
    with lang_col:
        st.selectbox("Answer Language", SUPPORTED_LANGUAGES, key="lang", index=SUPPORTED_LANGUAGES.index(st.session_state.lang), label_visibility="collapsed")
    with reset_col:
        if st.button("Start Over", on_click=reset_app_state, use_container_width=True): st.rerun()

    st.markdown("---")
    st.subheader("Document Interaction & AI Assistant")
    tab1, tab2, tab3 = st.tabs(["📄 Document View", "⚡ Actions", "💬 Ask AI"])

    with tab1:
        st.write(f"**Detected Document Type:** <span style='color:#00B4D8;'>{doc_type}</span>", unsafe_allow_html=True)
        st.info("Below is the combined, extracted text from all uploaded documents.")
        st.code(doc_text[:Config.MAX_DOCUMENT_LENGTH // 4] + "...", language="text")

    with tab2:
        st.write(f"**Document Type:** <span style='color:#00B4D8;'>{doc_type}</span>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        actions = {"key_info": ("Extract Key Information", ai_processor.extract_entities, "success"), "risk": ("Risk Assessment", ai_processor.perform_risk_analysis, "warning"), "explain": ("Explain Complex Terms", ai_processor.explain_complex_terms, "info"), "checklist": ("Compliance Checklist", ai_processor.generate_compliance_checklist, "success"), "summarize": ("Summarize Document", ai_processor.summarize_document, "success"), "simplify": ("Simplify Document", ai_processor.simplify_document, "info")}
        
        clicked_action = None
        for i, (key, (label, _, _)) in enumerate(actions.items()):
            col = col1 if i < 3 else col2
            if col.button(label, use_container_width=True, key=f"btn_{key}"):
                clicked_action = key

        if clicked_action:
            label, method, msg_type = actions[clicked_action]
            with st.spinner(f"Running {label}..."):
                result = method(doc_text, doc_type, st.session_state.lang)
                st.session_state.action_outputs[clicked_action] = {"type": msg_type, "header": f"{label} Results:", "content": result}
            st.rerun()

        if st.session_state.action_outputs:
            st.markdown("---")
            st.subheader("Results:")
            for output in st.session_state.action_outputs.values():
                getattr(st, output["type"])(output["header"])
                st.markdown(output["content"])

    with tab3:
        st.write("Ask questions about your document using our AI Assistant:")
        
        for entry in st.session_state.chat_history:
            with st.chat_message(entry["role"], avatar="🧑‍💻" if entry["role"] == "user" else "🤖"):
                st.markdown(entry["content"])
                if entry["role"] == "ai" and entry.get("context"):
                    with st.expander("Show Sources"):
                        st.info(entry["context"])
        
        if not st.session_state.chat_history:
            st.markdown("---")
            if 'suggested_questions' not in st.session_state:
                with st.spinner("Generating suggested questions..."):
                    st.session_state.suggested_questions = ai_processor.generate_suggested_questions(doc_text, doc_type, st.session_state.lang)
            
            if st.session_state.suggested_questions and isinstance(st.session_state.suggested_questions, list) and len(st.session_state.suggested_questions) > 0:
                st.markdown("**Suggested Questions:**")
                num_questions = len(st.session_state.suggested_questions)
                q_cols = st.columns(num_questions)
                for i in range(num_questions):
                    with q_cols[i]:
                        if st.button(st.session_state.suggested_questions[i], key=f"suggestion_{i}", use_container_width=True):
                            st.session_state.user_input_from_button = st.session_state.suggested_questions[i]
                            st.rerun()

        prompt = st.chat_input("Type your question or click a suggestion...")
        if "user_input_from_button" in st.session_state:
            prompt = st.session_state.user_input_from_button
            del st.session_state["user_input_from_button"]

        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.spinner("Finding answer in document..."):
                chat_service.set_document_context(doc_text, doc_type)
                response_dict = chat_service.ask_question(prompt, language=st.session_state.lang)
                ai_response = {
                    "role": "ai",
                    "content": response_dict.get("answer", "Sorry, I encountered an error."),
                    "context": response_dict.get("context")
                }
                st.session_state.chat_history.append(ai_response)
            st.rerun()
            
        if len(st.session_state.chat_history) > 0:
            st.markdown("---")
            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                if 'suggested_questions' in st.session_state:
                    del st.session_state['suggested_questions']
                st.rerun()

@st.cache_data
def render_footer():
    return '<div class="footer">Generative AI for Demystifying Healthcare Documents</div>'

st.markdown(render_footer(), unsafe_allow_html=True)