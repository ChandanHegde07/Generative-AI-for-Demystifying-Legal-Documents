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
    page_title="Healthcare Document AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_data
def get_custom_css():
    return """<style>
/* ==================== CSS RESET & MODERN BASE ==================== */
*, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, .main, .block-container {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    background-attachment: fixed;
    color: #E8EAF6;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    line-height: 1.7;
    scroll-behavior: smooth;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ==================== LAYOUT CONTAINER ==================== */
.block-container {
    max-width: 1600px !important;
    padding: 3rem 4rem !important;
    margin: 0 auto;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {
    visibility: hidden;
    display: none;
}

[data-testid="stSidebar"] {
    display: none;
}

/* ==================== TYPOGRAPHY SYSTEM ==================== */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 1.5rem;
    line-height: 1.2;
}

h1 { font-size: 3rem; }
h2 { font-size: 2.2rem; }
h3 { font-size: 1.6rem; }

p {
    font-size: 1.05rem;
    margin-bottom: 1rem;
    color: #E8EAF6 !important;
    line-height: 1.7;
}

strong {
    color: #FFFFFF !important;
    font-weight: 600;
}

/* Universal text visibility */
div, span, label, li {
    color: #E8EAF6 !important;
}

/* ==================== HERO HEADER ==================== */
.hero-header {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
    border: 2px solid rgba(102, 126, 234, 0.4);
    border-radius: 24px;
    padding: 3.5rem 2rem;
    text-align: center;
    margin-bottom: 3rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    backdrop-filter: blur(20px);
    animation: fadeInScale 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
    animation: rotate 20s linear infinite;
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.hero-header h1 {
    font-size: 3rem;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 20px rgba(102, 126, 234, 0.6);
    color: #FFFFFF !important;
    position: relative;
    z-index: 1;
}

.hero-header p {
    font-size: 1.2rem;
    color: #D1C4E9 !important;
    margin-top: 0.5rem;
    position: relative;
    z-index: 1;
}

@keyframes fadeInScale {
    from {
        opacity: 0;
        transform: scale(0.95) translateY(-20px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

/* ==================== UPLOAD SECTION ==================== */
.upload-section {
    background: rgba(255, 255, 255, 0.03);
    border: 2px solid rgba(102, 126, 234, 0.25);
    border-radius: 20px;
    padding: 3rem;
    margin: 2rem 0;
    text-align: center;
    min-height: 380px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    backdrop-filter: blur(10px);
}

div[data-testid="stFileUploader"] {
    border: 3px dashed rgba(102, 126, 234, 0.5);
    border-radius: 20px;
    background: rgba(102, 126, 234, 0.06);
    padding: 3rem 2rem;
    min-height: 240px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(5px);
    width: 100%;
    max-width: 900px;
    margin: 0 auto;
}

div[data-testid="stFileUploader"]:hover {
    border-color: rgba(245, 87, 108, 0.7);
    background: rgba(245, 87, 108, 0.08);
    transform: translateY(-4px);
    box-shadow: 0 15px 40px rgba(245, 87, 108, 0.25);
}

.stFileUploader label {
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    margin-bottom: 1.5rem !important;
    display: block !important;
}

div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] p,
div[data-testid="stFileUploader"] div,
div[data-testid="stFileUploader"] span {
    color: #D1C4E9 !important;
}

.stFileUploader button {
    padding: 1rem 3rem !important;
    font-size: 1.1rem !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 700 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4) !important;
}

.stFileUploader button:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 30px rgba(102, 126, 234, 0.6) !important;
}

/* ==================== SELECT BOXES - PERFECT ALIGNMENT ==================== */
div[data-testid="stSelectbox"] {
    margin: 0 !important;
}

div[data-testid="stSelectbox"] > label {
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: #FFFFFF !important;
    margin-bottom: 0.75rem !important;
    display: block !important;
}

/* Select box container with fixed height */
div[data-testid="stSelectbox"] > div {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 2px solid rgba(102, 126, 234, 0.4) !important;
    border-radius: 12px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    min-height: 50px !important;
    height: 50px !important;
    display: flex !important;
    align-items: center !important;
}

/* Selected value - WHITE TEXT */
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stSelectbox"] > div > div > div,
div[data-testid="stSelectbox"] [role="button"],
div[data-testid="stSelectbox"] input {
    color: #FFFFFF !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    background: transparent !important;
    padding: 0.8rem 1.2rem !important;
}

/* Dropdown arrow */
div[data-testid="stSelectbox"] svg {
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
    width: 20px !important;
    height: 20px !important;
}

div[data-testid="stSelectbox"] > div:hover {
    border-color: rgba(245, 87, 108, 0.6) !important;
    box-shadow: 0 4px 15px rgba(245, 87, 108, 0.25) !important;
    background: rgba(255, 255, 255, 0.12) !important;
}

/* Dropdown menu */
div[role="listbox"] {
    background: #2A2440 !important;
    border: 2px solid rgba(102, 126, 234, 0.5) !important;
    border-radius: 12px !important;
    margin-top: 0.5rem !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5) !important;
}

div[role="option"] {
    color: #E8EAF6 !important;
    padding: 0.9rem 1.2rem !important;
    background: transparent !important;
    transition: all 0.2s ease !important;
}

div[role="option"]:hover {
    background: rgba(102, 126, 234, 0.4) !important;
    color: #FFFFFF !important;
}

div[role="option"][aria-selected="true"] {
    background: rgba(102, 126, 234, 0.3) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* ==================== BUTTONS - PERFECT ALIGNMENT ==================== */
.stButton {
    width: 100%;
    display: flex !important;
    align-items: center !important;
}

.stButton > button {
    padding: 0 2rem !important;
    font-size: 1.05rem !important;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 6px 18px rgba(245, 87, 108, 0.4) !important;
    width: 100% !important;
    min-height: 50px !important;
    height: 50px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 25px rgba(245, 87, 108, 0.6) !important;
}

.stButton > button:active {
    transform: translateY(-1px) !important;
}

/* ==================== TABS - MODERN DESIGN ==================== */
.stTabs {
    margin-top: 2.5rem;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
    background: rgba(255, 255, 255, 0.04);
    padding: 1rem;
    border-radius: 16px;
    border: 1px solid rgba(102, 126, 234, 0.2);
}

.stTabs [data-baseweb="tab"] {
    padding: 1rem 2.5rem !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    background: rgba(255, 255, 255, 0.06) !important;
    border-radius: 12px !important;
    color: #D1C4E9 !important;
    border: 2px solid transparent !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(102, 126, 234, 0.15) !important;
    border-color: rgba(102, 126, 234, 0.4) !important;
    color: #FFFFFF !important;
    transform: translateY(-2px);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border-color: rgba(102, 126, 234, 0.6) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    transform: translateY(-2px);
}

.stTabs [data-baseweb="tab-panel"] {
    padding: 2.5rem 1rem !important;
}

/* ==================== STATUS & ALERTS ==================== */
div[data-testid="stStatus"] {
    background: rgba(102, 126, 234, 0.12) !important;
    border: 2px solid rgba(102, 126, 234, 0.3) !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    backdrop-filter: blur(10px) !important;
}

div[data-testid="stStatus"] p,
div[data-testid="stStatus"] div,
div[data-testid="stStatus"] span {
    color: #E8EAF6 !important;
}

.stAlert {
    padding: 1.2rem 1.5rem !important;
    border-radius: 12px !important;
    font-size: 1.05rem !important;
    border-left: 4px solid !important;
    margin: 1.5rem 0 !important;
    backdrop-filter: blur(10px) !important;
}

.stAlert p, .stAlert div {
    color: #E8EAF6 !important;
}

div[data-testid="stNotification"] {
    background: rgba(102, 126, 234, 0.12) !important;
    border: 1px solid rgba(102, 126, 234, 0.3) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
}

div[data-testid="stNotification"] p,
div[data-testid="stNotification"] div {
    color: #E8EAF6 !important;
}

/* ==================== CHAT INTERFACE ==================== */
.stChatMessage {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(102, 126, 234, 0.25) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    margin: 1rem 0 !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    backdrop-filter: blur(10px) !important;
}

.stChatMessage p,
.stChatMessage div,
.stChatMessage span {
    color: #E8EAF6 !important;
}

.stChatInput {
    margin: 2rem auto !important;
    max-width: 100% !important;
}

.stChatInput > div {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 2px solid rgba(102, 126, 234, 0.4) !important;
    border-radius: 15px !important;
}

.stChatInput input,
.stChatInput textarea {
    color: #FFFFFF !important;
}

/* ==================== CODE BLOCKS ==================== */
.stCodeBlock {
    background: rgba(0, 0, 0, 0.5) !important;
    border: 1px solid rgba(102, 126, 234, 0.3) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    margin: 1.5rem 0 !important;
}

.stCodeBlock code {
    color: #E8EAF6 !important;
}

pre {
    background: rgba(0, 0, 0, 0.5) !important;
    color: #E8EAF6 !important;
}

/* ==================== EXPANDER ==================== */
.stExpander {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(102, 126, 234, 0.25) !important;
    border-radius: 12px !important;
    margin: 1rem 0 !important;
    backdrop-filter: blur(5px) !important;
}

.stExpander summary {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

.stExpander p,
.stExpander div,
.stExpander span {
    color: #E8EAF6 !important;
}

/* ==================== SPINNER ==================== */
div[data-testid="stSpinner"] p,
div[data-testid="stSpinner"] div,
div[data-testid="stSpinner"] span {
    color: #D1C4E9 !important;
}

/* ==================== FOOTER ==================== */
.custom-footer {
    margin-top: 4rem;
    padding: 2rem;
    text-align: center;
    background: rgba(255, 255, 255, 0.03);
    border: 2px solid rgba(102, 126, 234, 0.25);
    border-radius: 20px;
    backdrop-filter: blur(15px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.custom-footer p {
    font-size: 1rem;
    color: #D1C4E9 !important;
    margin: 0;
}

/* ==================== HORIZONTAL RULE ==================== */
hr {
    border: none;
    border-top: 2px solid rgba(102, 126, 234, 0.25);
    margin: 3rem 0;
}

/* ==================== MARKDOWN TEXT ==================== */
.stMarkdown p,
.stMarkdown div,
.stMarkdown span,
.stMarkdown li {
    color: #E8EAF6 !important;
}

/* ==================== RESPONSIVE DESIGN ==================== */
@media (min-width: 1920px) {
    .block-container {
        max-width: 1920px !important;
        padding: 4rem 6rem !important;
    }
    .hero-header h1 {
        font-size: 3.5rem;
    }
}

@media (max-width: 1400px) {
    .block-container {
        padding: 2.5rem 3rem !important;
    }
    .hero-header h1 {
        font-size: 2.5rem;
    }
}

@media (max-width: 768px) {
    .block-container {
        padding: 1.5rem !important;
    }
    .hero-header {
        padding: 2rem 1rem;
    }
    .hero-header h1 {
        font-size: 2rem;
    }
    div[data-testid="stFileUploader"] {
        padding: 2rem 1rem;
        min-height: 200px;
    }
    h2 {
        font-size: 1.6rem;
    }
}

/* ==================== ANIMATIONS ==================== */
@keyframes fadeIn {
    from { 
        opacity: 0; 
        transform: translateY(10px); 
    }
    to { 
        opacity: 1; 
        transform: translateY(0); 
    }
}

.stApp > div {
    animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ==================== SCROLLBAR ==================== */
::-webkit-scrollbar {
    width: 12px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.3);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 6px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

/* ==================== UTILITIES ==================== */
.glass-effect {
    backdrop-filter: blur(10px);
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
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
        'uploaded_files_key': 0, 
        'rag_service': None
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

st.markdown("""
<div class="hero-header">
    <h1>🏥 Healthcare Document AI Assistant</h1>
    <p>Demystifying medical documents with advanced AI technology</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.document_processed:
    st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "📁 Upload Your Healthcare Documents", 
        type=["pdf", "jpg", "jpeg", "png", "txt"], 
        accept_multiple_files=True, 
        key=f"file_uploader_{st.session_state.uploaded_files_key}",
        help="Drag and drop files here or click to browse. Supports PDF, JPG, JPEG, PNG, TXT (Max 200MB per file)"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.session_state.lang = st.selectbox(
            "🌐 Select Answer Language", 
            SUPPORTED_LANGUAGES, 
            key="lang_select_initial", 
            index=SUPPORTED_LANGUAGES.index(st.session_state.lang)
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.info("💡 **Tip:** Upload one or more documents. Our AI will analyze and combine their content for comprehensive insights.")

    if uploaded_files:
        with st.status(f"🔄 Processing {len(uploaded_files)} document(s)...", expanded=True) as status:
            all_texts, errors = [], []
            for up_file in uploaded_files:
                st.write(f"📄 Extracting text from `{up_file.name}`...")
                try:
                    is_valid, msg = Config.validate_file(up_file)
                    if not is_valid:
                        errors.append(f"❌ '{up_file.name}' is invalid: {msg}")
                        continue
                    up_file.seek(0)
                    text = doc_parser.extract_text_from_file(up_file)
                    is_valid, msg = doc_parser.validate_extracted_text(text)
                    if not is_valid:
                        errors.append(f"❌ Could not process '{up_file.name}': {msg}")
                    else:
                        all_texts.append(text)
                        st.write(f"✅ Successfully processed `{up_file.name}`")
                except Exception as e:
                    errors.append(f"❌ Error with `{up_file.name}`: {e}")
            
            for error in errors: 
                st.error(error)
            
            if all_texts:
                st.write("🔍 Analyzing document content...")
                doc_text = doc_parser.preprocess_text("\n\n".join(all_texts))
                classification = ai_processor.classify_document(doc_text)
                doc_type = classification.get("document_type", "Other")
                st.write("🗂️ Creating searchable index for Q&A...")
                rag_service = RAGService(doc_text)
                st.session_state.update({
                    'document_text': doc_text, 
                    'doc_type': doc_type, 
                    'document_processed': True, 
                    'rag_service': rag_service, 
                    'chat_history': [], 
                    'action_outputs': {}
                })
                status.update(label="✅ Processing Complete!", state="complete", expanded=False)
                st.rerun()
            else:
                status.update(label="❌ Processing Failed", state="error", expanded=True)
                if not errors: 
                    st.error("No meaningful text could be extracted from the uploaded documents.")

else:
    doc_text, doc_type = st.session_state.document_text, st.session_state.doc_type
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_spacer1, col_lang, col_button, col_spacer2 = st.columns([1, 2, 2, 1])
    
    with col_lang:
        st.selectbox(
            "🌐 Answer Language", 
            SUPPORTED_LANGUAGES, 
            key="lang", 
            index=SUPPORTED_LANGUAGES.index(st.session_state.lang)
        )
        
    with col_button:
        if st.button("🔄 Start Over", use_container_width=True): 
            reset_app_state()
            st.rerun()

    st.markdown("---")

    # Main Tabs
    tab1, tab2, tab3 = st.tabs(["📄 Document View", "⚡ AI Actions", "💬 Ask Questions"])

    with tab1:
        st.markdown("### Document Information")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**📋 Document Type:** {doc_type}")
        with col2:
            st.info(f"**📏 Document Length:** {len(doc_text):,} characters")
        
        st.markdown("### 📖 Extracted Text Preview")
        st.code(doc_text[:Config.MAX_DOCUMENT_LENGTH // 2] + "\n\n... [Content continues]", language="text")

    with tab2:
        st.markdown("### AI-Powered Document Analysis")
        st.write(f"**Current Document Type:** `{doc_type}`")
        
        col1, col2, col3 = st.columns(3)
        
        actions = {
            "key_info": ("📊 Extract Key Info", ai_processor.extract_entities, "success"), 
            "risk": ("⚠️ Risk Assessment", ai_processor.perform_risk_analysis, "warning"), 
            "explain": ("📖 Explain Terms", ai_processor.explain_complex_terms, "info"), 
            "checklist": ("✅ Compliance Check", ai_processor.generate_compliance_checklist, "success"), 
            "summarize": ("📝 Summarize", ai_processor.summarize_document, "success"), 
            "simplify": ("🔍 Simplify", ai_processor.simplify_document, "info")
        }
        
        clicked_action = None
        for i, (key, (label, _, _)) in enumerate(actions.items()):
            col = [col1, col2, col3][i % 3]
            if col.button(label, use_container_width=True, key=f"btn_{key}"):
                clicked_action = key

        if clicked_action:
            label, method, msg_type = actions[clicked_action]
            with st.spinner(f"🔄 Running {label}..."):
                result = method(doc_text, doc_type, st.session_state.lang)
                st.session_state.action_outputs[clicked_action] = {
                    "type": msg_type, 
                    "header": f"{label} Results", 
                    "content": result
                }
            st.rerun()

        if st.session_state.action_outputs:
            st.markdown("---")
            st.markdown("### 📊 Analysis Results")
            for output in st.session_state.action_outputs.values():
                getattr(st, output["type"])(f"**{output['header']}**")
                st.markdown(output["content"])

    with tab3:
        st.markdown("### 💬 Interactive Q&A Assistant")
        
        for entry in st.session_state.chat_history:
            with st.chat_message(entry["role"], avatar="👤" if entry["role"] == "user" else "🤖"):
                st.markdown(entry["content"])
                if entry["role"] == "ai" and entry.get("context"):
                    with st.expander("📚 View Source Context"):
                        st.info(entry["context"])
        
        if not st.session_state.chat_history:
            if 'suggested_questions' not in st.session_state:
                with st.spinner("🔮 Generating intelligent question suggestions..."):
                    st.session_state.suggested_questions = ai_processor.generate_suggested_questions(
                        doc_text, doc_type, st.session_state.lang
                    )
            
            if st.session_state.suggested_questions and isinstance(st.session_state.suggested_questions, list):
                st.markdown("#### 💡 Suggested Questions")
                for i, question in enumerate(st.session_state.suggested_questions[:4]):
                    if st.button(f"💬 {question}", key=f"suggestion_{i}", use_container_width=True):
                        st.session_state.user_input_from_button = question
                        st.rerun()

        prompt = st.chat_input("💭 Type your question here...")
        if "user_input_from_button" in st.session_state:
            prompt = st.session_state.user_input_from_button
            del st.session_state["user_input_from_button"]

        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.spinner("🔍 Searching document for answer..."):
                chat_service.set_document_context(doc_text, doc_type)
                response_dict = chat_service.ask_question(prompt, language=st.session_state.lang)
                ai_response = {
                    "role": "ai",
                    "content": response_dict.get("answer", "I apologize, but I encountered an error processing your question."),
                    "context": response_dict.get("context")
                }
                st.session_state.chat_history.append(ai_response)
            st.rerun()
            
        if len(st.session_state.chat_history) > 0:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🗑️ Clear Chat History", use_container_width=True):
                    st.session_state.chat_history = []
                    if 'suggested_questions' in st.session_state:
                        del st.session_state['suggested_questions']
                    st.rerun()

# Footer
st.markdown("""
<div class="custom-footer">
    <p>🏥 <strong>Healthcare Document AI Assistant</strong> | Powered by Advanced Generative AI | Secure & Confidential</p>
</div>
""", unsafe_allow_html=True)
