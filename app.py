import streamlit as st
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
import re
from typing import List, Any, Dict
import io
from datetime import datetime
from functools import lru_cache
import hashlib

from src.config import Config
from src.services.ai_processor import AIProcessor
from src.services.chat_service import ChatService
from src.services.rag_service import RAGService
from src.utils.document_parser import DocumentParser
from src.utils.translator import GeminiTranslator

# --- Service Initialization ---
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
    page_title="Legal & Healthcare Document AI Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="auto" 
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
    background: linear-gradient(135deg, #0a0118 0%, #1a0d2e 50%, #16003b 100%);
    background-attachment: fixed;
    color: #FFFFFF;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    line-height: 1.7;
    scroll-behavior: smooth;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Animated particles background */
body::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: 
        radial-gradient(circle at 20% 50%, rgba(0, 245, 255, 0.12) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(192, 38, 211, 0.12) 0%, transparent 50%),
        radial-gradient(circle at 40% 80%, rgba(192, 38, 211, 0.08) 0%, transparent 50%);
    animation: rotate 30s linear infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* ==================== LAYOUT CONTAINER ==================== */
.block-container {
    max-width: 1600px !important;
    padding: 3rem 4rem !important;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {
    visibility: hidden;
    display: none;
}

/* --- MODIFIED: Allows your sidebar report page to show --- */
/*
[data-testid="stSidebar"] {
    display: none;
}
*/

/* ==================== CRITICAL TEXT VISIBILITY FIXES ==================== */
/* Base text colors - CRITICAL */
div, span, label, li, p, input, textarea, select, option {
    color: #FFFFFF !important;
}

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

strong {
    color: #FFFFFF !important;
    font-weight: 600;
}

/* ==================== HERO HEADER ==================== */
.hero-header {
    background: linear-gradient(135deg, rgba(0, 245, 255, 0.08) 0%, rgba(192, 38, 211, 0.08) 100%);
    border: 2px solid rgba(0, 245, 255, 0.3);
    border-radius: 28px;
    padding: 3.5rem 2rem;
    text-align: center;
    margin-bottom: 3rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    backdrop-filter: blur(30px);
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
    background: radial-gradient(circle, rgba(0, 245, 255, 0.1) 0%, transparent 70%);
    animation: rotate 20s linear infinite;
}

.hero-header h1 {
    font-size: 3rem;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 20px rgba(0, 245, 255, 0.6);
    background: linear-gradient(135deg, #00F5FF 0%, #C026D3 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    position: relative;
    z-index: 1;
}

.hero-header p {
    font-size: 1.2rem;
    color: #B4B4D4 !important;
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
    background: rgba(255, 255, 255, 0.04);
    border: 2px solid rgba(0, 245, 255, 0.25);
    border-radius: 24px;
    padding: 3rem;
    margin: -50rem 0;
    text-align: center;
    min-height: 380px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    backdrop-filter: blur(15px);
}

div[data-testid="stFileUploader"] {
    border: 3px dashed rgba(0, 245, 255, 0.4);
    border-radius: 20px;
    background: rgba(0, 245, 255, 0.04);
    padding: 3rem 2rem;
    min-height: 240px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
    width: 100%;
    max-width: 900px;
    margin: 0 auto;
}

div[data-testid="stFileUploader"]:hover {
    border-color: rgba(192, 38, 211, 0.6);
    background: rgba(192, 38, 211, 0.06);
    transform: translateY(-4px);
    box-shadow: 0 15px 40px rgba(192, 38, 211, 0.25);
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
    color: #B4B4D4 !important;
}

.stFileUploader button {
    padding: 1rem 3rem !important;
    font-size: 1.1rem !important;
    background: linear-gradient(135deg, #00F5FF 0%, #C026D3 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 700 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 8px 20px rgba(0, 245, 255, 0.4) !important;
}

.stFileUploader button:hover {
    background: linear-gradient(135deg, #C026D3 0%, #00F5FF 100%) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 30px rgba(192, 38, 211, 0.5) !important;
}

/* ==================== SELECT BOXES - FIXED VISIBILITY & ALIGNMENT ==================== */
div[data-testid="stSelectbox"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* Label - WHITE and BOLD with consistent spacing */
div[data-testid="stSelectbox"] > label,
div[data-testid="stSelectbox"] label {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    margin-bottom: 0.75rem !important;
    margin-top: 0 !important;
    display: block !important;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5) !important;
    height: auto !important;
    line-height: 1.4 !important;
}

/* Select box container - EXACT HEIGHT MATCH */
div[data-testid="stSelectbox"] > div,
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stSelectbox"] [data-baseweb="select"] {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 2px solid rgba(0, 245, 255, 0.4) !important;
    border-radius: 14px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    min-height: 56px !important;
    height: 56px !important;
    max-height: 56px !important;
    display: flex !important;
    align-items: center !important;
    backdrop-filter: blur(10px) !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Selected value - BRIGHT WHITE TEXT with shadow */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div > div,
div[data-testid="stSelectbox"] [role="button"],
div[data-testid="stSelectbox"] [data-baseweb="select"] [role="button"] > div,
div[data-testid="stSelectbox"] input,
div[data-testid="stSelectbox"] span {
    color: #FFFFFF !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    background: transparent !important;
    padding: 0.8rem 1.2rem !important;
    text-shadow: 0 2px 6px rgba(0, 0, 0, 0.4) !important;
    line-height: 1.5 !important;
}

/* Dropdown arrow - WHITE */
div[data-testid="stSelectbox"] svg,
div[data-testid="stSelectbox"] svg path {
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
    width: 22px !important;
    height: 22px !important;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3)) !important;
}

div[data-testid="stSelectbox"] > div:hover,
div[data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(192, 38, 211, 0.6) !important;
    box-shadow: 0 4px 20px rgba(192, 38, 211, 0.3) !important;
    background: rgba(255, 255, 255, 0.15) !important;
}

/* Dropdown menu */
div[role="listbox"],
ul[role="listbox"] {
    background: #1a0d2e !important;
    border: 2px solid rgba(0, 245, 255, 0.5) !important;
    border-radius: 14px !important;
    margin-top: 0.5rem !important;
    box-shadow: 0 10px 50px rgba(0, 0, 0, 0.7) !important;
    backdrop-filter: blur(20px) !important;
}

div[role="option"],
li[role="option"] {
    color: #FFFFFF !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    padding: 1rem 1.5rem !important;
    background: transparent !important;
    transition: all 0.2s ease !important;
}

div[role="option"]:hover,
li[role="option"]:hover {
    background: rgba(0, 245, 255, 0.2) !important;
    color: #FFFFFF !important;
}

div[role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"] {
    background: rgba(0, 245, 255, 0.3) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* ==================== BUTTONS - PERFECT ALIGNMENT ==================== */
.stButton {
    width: 100%;
    display: flex !important;
    align-items: flex-end !important;
    margin: 0 !important;
    padding: 0 !important;
}

.stButton > button {
    padding: 0 2rem !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #00F5FF 0%, #C026D3 100%) !important;
    border: none !important;
    border-radius: 14px !important;
    color: white !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 6px 20px rgba(0, 245, 255, 0.4) !important;
    width: 100% !important;
    min-height: 56px !important;
    height: 56px !important;
    max-height: 56px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
    margin: 0 !important;
}

/* This is a special fix for the Start Over button to align with the select box */
/* We target the button inside the column specifically */
[data-testid="stVerticalBlock"] [data-testid="stHorizontalBlock"] .stButton {
    margin-top: 2.15rem !important;
}


.stButton > button:hover {
    background: linear-gradient(135deg, #C026D3 0%, #00F5FF 100%) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 30px rgba(192, 38, 211, 0.5) !important;
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
    border: 1px solid rgba(0, 245, 255, 0.2);
}

.stTabs [data-baseweb="tab"] {
    padding: 1rem 2.5rem !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    background: rgba(255, 255, 255, 0.06) !important;
    border-radius: 12px !important;
    color: #B4B4D4 !important;
    border: 2px solid transparent !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(0, 245, 255, 0.1) !important;
    border-color: rgba(0, 245, 255, 0.4) !important;
    color: #FFFFFF !important;
    transform: translateY(-2px);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #00F5FF 0%, #C026D3 100%) !important;
    color: white !important;
    border-color: rgba(0, 245, 255, 0.6) !important;
    box-shadow: 0 8px 25px rgba(0, 245, 255, 0.4) !important;
    transform: translateY(-2px);
}

.stTabs [data-baseweb="tab-panel"] {
    padding: 2.5rem 1rem !important;
}

/* ==================== STATUS & ALERTS ==================== */
div[data-testid="stStatus"] {
    background: rgba(0, 245, 255, 0.08) !important;
    border: 2px solid rgba(0, 245, 255, 0.3) !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    backdrop-filter: blur(10px) !important;
}

div[data-testid="stStatus"] p,
div[data-testid="stStatus"] div,
div[data-testid="stStatus"] span {
    color: #FFFFFF !important;
}

.stAlert {
    padding: 1.2rem 1.5rem !important;
    border-radius: 12px !important;
    font-size: 1.05rem !important;
    border-left: 4px solid !important;
    margin: 1.5rem 0 !important;
    backdrop-filter: blur(10px) !important;
}

.stAlert p, .stAlert div, .stAlert span {
    color: #FFFFFF !important;
}

div[data-testid="stNotification"] {
    background: rgba(0, 245, 255, 0.08) !important;
    border: 1px solid rgba(0, 245, 255, 0.3) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
}

div[data-testid="stNotification"] p,
div[data-testid="stNotification"] div,
div[data-testid="stNotification"] span {
    color: #FFFFFF !important;
}

/* Info boxes */
div[data-testid="stInfo"],
.stInfo {
    background: rgba(0, 245, 255, 0.08) !important;
    border: 1px solid rgba(0, 245, 255, 0.3) !important;
    color: #FFFFFF !important;
}

div[data-testid="stInfo"] p,
div[data-testid="stInfo"] div,
div[data-testid="stInfo"] span,
.stInfo p,
.stInfo div,
.stInfo span {
    color: #FFFFFF !important;
}

/* ==================== CHAT INTERFACE ==================== */
.stChatMessage {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(0, 245, 255, 0.25) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    margin: 1rem 0 !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    backdrop-filter: blur(10px) !important;
}

.stChatMessage p,
.stChatMessage div,
.stChatMessage span {
    color: #FFFFFF !important;
}

.stChatInput {
    margin: 2rem auto !important;
    max-width: 100% !important;
}

.stChatInput > div {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 2px solid rgba(0, 245, 255, 0.4) !important;
    border-radius: 15px !important;
}

.stChatInput input,
.stChatInput textarea {
    color: #FFFFFF !important;
}

/* ==================== CODE BLOCKS ==================== */
.stCodeBlock {
    background: rgba(0, 0, 0, 0.5) !important;
    border: 1px solid rgba(0, 245, 255, 0.3) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    margin: 1.5rem 0 !important;
}

.stCodeBlock code {
    color: #FFFFFF !important;
}

pre {
    background: rgba(0, 0, 0, 0.5) !important;
    color: #FFFFFF !important;
}

code {
    color: #FFFFFF !important;
}

/* ==================== EXPANDER ==================== */
.stExpander {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(0, 245, 255, 0.25) !important;
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
    color: #FFFFFF !important;
}

/* ==================== SPINNER ==================== */
div[data-testid="stSpinner"] p,
div[data-testid="stSpinner"] div,
div[data-testid="stSpinner"] span {
    color: #FFFFFF !important;
}

/* ==================== MARKDOWN TEXT ==================== */
.stMarkdown p,
.stMarkdown div,
.stMarkdown span,
.stMarkdown li {
    color: #FFFFFF !important;
}

/* ==================== FOOTER ==================== */
.custom-footer {
    margin-top: 4rem;
    padding: 2rem;
    text-align: center;
    background: rgba(255, 255, 255, 0.03);
    border: 2px solid rgba(0, 245, 255, 0.25);
    border-radius: 20px;
    backdrop-filter: blur(15px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.custom-footer p {
    font-size: 1rem;
    color: #B4B4D4 !important;
    margin: 0;
}

/* ==================== HORIZONTAL RULE ==================== */
hr {
    border: none;
    border-top: 2px solid rgba(0, 245, 255, 0.25);
    margin: 3rem 0;
}

/* ==================== SCROLLBAR ==================== */
::-webkit-scrollbar {
    width: 12px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.3);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #00F5FF 0%, #C026D3 100%);
    border-radius: 6px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #C026D3 0%, #00F5FF 100%);
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
        'rag_service': None,
        'financial_rules': None,
        'suggested_questions': [],
        'show_summary_options': False,
        'summary_result': None,
        'action_history': []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

def reset_app_state():
    """
    Clears all cache data and session state to start fresh.
    """
    st.cache_data.clear()
    st.cache_resource.clear()
    
    current_key = st.session_state.get('uploaded_files_key', 0)
    st.session_state.clear()
    
    init_session_state()
    st.session_state.uploaded_files_key = current_key + 1

@st.cache_data(show_spinner=False)
def run_classification(document_text):
    return ai_processor.classify_document(document_text)

@st.cache_data(show_spinner=False)
def run_question_generation(_document_text, _doc_type, _lang): 
    questions_json = ai_processor.generate_suggested_questions(_document_text, _doc_type, _lang) 
    try:
        loaded_json = json.loads(questions_json)
        if isinstance(loaded_json, list) and all(isinstance(item, str) for item in loaded_json):
            return loaded_json
        else:
            return []
    except:
        return []

@st.cache_data(show_spinner=False)
def run_extract_entities(_document_text, _doc_type, _lang):
    return ai_processor.extract_entities(_document_text, _doc_type, _lang)

@st.cache_data(show_spinner=False)
def run_risk_analysis(_document_text, _doc_type, _lang):
    return ai_processor.perform_risk_analysis(_document_text, _doc_type, _lang)

@st.cache_data(show_spinner=False)
def run_explain_terms(_document_text, _doc_type, _lang):
    return ai_processor.explain_complex_terms(_document_text, _doc_type, _lang)

@st.cache_data(show_spinner=False)
def run_compliance_checklist(_document_text, _doc_type, _lang):
    return ai_processor.generate_compliance_checklist(_document_text, _doc_type, _lang)

@st.cache_data(show_spinner=False)
def run_simplify_document(_document_text, _doc_type, _lang):
    return ai_processor.simplify_document(_document_text, _doc_type, _lang)

@st.cache_data(show_spinner=False)
def run_get_summary(_document_text, _doc_type, _lang, summary_type):
    return ai_processor.get_summary(_document_text, _doc_type, _lang, summary_type)

@st.cache_data(show_spinner=False)
def run_cost_calculation(rules_str, user_costs_str, doc_type):
    return ai_processor.calculate_cost_liability(rules_str, user_costs_str, doc_type)

def create_risk_meter(risk_score, risk_level):
    fig = px.pie(values=[risk_score, 100 - risk_score], names=['Risk', ''], hole=0.6, color_discrete_sequence=["#FF4B4B", "rgba(0,0,0,0)"])
    fig.update_traces(textinfo='none', marker=dict(line=dict(width=0)))
    fig.update_layout(title=f"<b>Risk Level: {risk_level.upper()}</b>", showlegend=False, width=250, height=250, margin=dict(t=60, b=10, l=10, r=10), annotations=[dict(text=f'<b>{risk_score}%</b>', x=0.5, y=0.5, font_size=32, showarrow=False)], plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#FFFFFF"))
    return fig

def log_action(action_name, action_type, output):
    st.session_state.action_history.insert(0, {
        "action": action_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": action_type,
        "output": output
    })


st.markdown("""
<div class="hero-header">
    <h1>Healthcare Document AI Assistant</h1>
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
    
    st.info("**Tip:** Upload one or more documents. Our AI will analyze and combine their content for comprehensive insights.")

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
                        st.write(f"Successfully processed `{up_file.name}`")
                except Exception as e:
                    errors.append(f"Error with `{up_file.name}`: {e}")
            
            for error in errors: 
                st.error(error)
            
            if all_texts:
                st.write("Analyzing document content...")
                doc_text = doc_parser.preprocess_text("\n\n".join(all_texts))
                classification = run_classification(doc_text)
                doc_type = classification.get("document_type", "Other")
                
                st.write("Creating searchable index for Q&A...")
                rag_service = RAGService(doc_text) 
                
                st.write("Generating intelligent question suggestions...")
                suggested_questions = run_question_generation(doc_text, doc_type, st.session_state.lang)
                
                st.session_state.update({
                    'document_text': doc_text, 
                    'doc_type': doc_type, 
                    'document_processed': True, 
                    'rag_service': rag_service, 
                    'chat_history': [], 
                    'action_outputs': {},
                    'suggested_questions': suggested_questions 
                })
                status.update(label="Processing Complete!", state="complete", expanded=False)
                st.rerun()
            else:
                status.update(label="Processing Failed", state="error", expanded=True)
                if not errors: 
                    st.error("No meaningful text could be extracted from the uploaded documents.")

else:
    doc_text = st.session_state.document_text
    doc_type = st.session_state.doc_type
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_lang, col_button = st.columns(2)
    
    with col_lang:
        st.selectbox(
            "🌐 Answer Language", 
            SUPPORTED_LANGUAGES, 
            key="lang", 
            index=SUPPORTED_LANGUAGES.index(st.session_state.lang)
        )
        
    with col_button:
        if st.button("Start Over", use_container_width=True, on_click=reset_app_state): 
            pass 

    st.markdown("---")

    dash_tab, sim_tab, chat_tab, doc_tab = st.tabs(["Dashboard", " Cost Simulator", "AI Chat", "Document View"])

    with dash_tab:
        st.subheader("AI Actions Dashboard")
        st.write("Click an action to get instant, graphical insights from your document.")
        st.markdown("---")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Extract Key Information", use_container_width=True):
                with st.spinner("Extracting and structuring key entities..."):
                    st.session_state.show_summary_options = False
                    result = run_extract_entities(st.session_state.document_text, st.session_state.doc_type, st.session_state.lang)
                    st.session_state.action_outputs = {"key_info": result}
                    log_action("Extract Key Information", "key_info", result)
            if st.button("Summarize Document", use_container_width=True):
                st.session_state.show_summary_options = True
                st.session_state.action_outputs = {}
                st.session_state.summary_result = None
        
        with col2:
            if st.button("Risk Assessment", use_container_width=True):
                with st.spinner("Building risk dashboard..."):
                    st.session_state.show_summary_options = False
                    result = run_risk_analysis(st.session_state.document_text, st.session_state.doc_type, st.session_state.lang)
                    st.session_state.action_outputs = {"risk": result}
                    log_action("Risk Assessment", "risk", result)
            if st.button("Explain Complex Terms", use_container_width=True):
                with st.spinner("Defining complex terms..."):
                    st.session_state.show_summary_options = False
                    result = run_explain_terms(st.session_state.document_text, st.session_state.doc_type, st.session_state.lang)
                    st.session_state.action_outputs = {"explain": result}
                    log_action("Explain Complex Terms", "explain", result)
        with col3:
            if st.button("Generate Compliance Checklist", use_container_width=True):
                with st.spinner("Building compliance scorecard..."):
                    st.session_state.show_summary_options = False
                    result = run_compliance_checklist(st.session_state.document_text, st.session_state.doc_type, st.session_state.lang)
                    st.session_state.action_outputs = {"checklist": result}
                    log_action("Generate Compliance Checklist", "checklist", result)
            if st.button("Simplify Document", use_container_width=True):
                with st.spinner("Translating to plain language..."):
                    st.session_state.show_summary_options = False
                    result = run_simplify_document(st.session_state.document_text, st.session_state.doc_type, st.session_state.lang)
                    st.session_state.action_outputs = {"simplify": result}
                    log_action("Simplify Document", "simplify", result)

        if st.session_state.action_outputs or st.session_state.show_summary_options:
            st.markdown("<hr style='margin-top: 2em; border-top: 2px solid rgba(0, 245, 255, 0.25);'>", unsafe_allow_html=True)
            st.subheader("AI-Generated Insights")
            
            if st.session_state.show_summary_options:
                with st.container(border=True):
                    st.markdown("### 📜 Visual & Textual Summary")
                    wc_col, opt_col = st.columns([1, 1.5])
                    with wc_col:
                        with st.spinner("Generating word cloud..."):
                            try:
                                wordcloud = WordCloud(width=400, height=300, background_color=None, mode="RGBA", colormap='viridis', max_words=75).generate(st.session_state.document_text)
                                fig, ax = plt.subplots()
                                fig.patch.set_alpha(0.0)
                                ax.patch.set_alpha(0.0)  
                                ax.imshow(wordcloud, interpolation='bilinear')
                                ax.axis("off")
                                st.pyplot(fig)
                            except Exception as e:
                                st.error(f"Could not generate word cloud: {e}")
                    with opt_col:
                        st.write("Choose the type of summary you need:")
                        btn_cols_row1 = st.columns(3)
                        if btn_cols_row1[0].button("Key Points"):
                            with st.spinner("Generating key points..."):
                                result = run_get_summary(st.session_state.document_text, st.session_state.doc_type, st.session_state.lang, "key_points")
                                st.session_state.summary_result = result
                                log_action("📜 Summary: Key Points", "summary_key_points", result)
                        if btn_cols_row1[1].button("Detailed Summary"):
                            with st.spinner("Generating detailed summary..."):
                                result = run_get_summary(st.session_state.document_text, st.session_state.doc_type, st.session_state.lang, "detailed")
                                st.session_state.summary_result = result
                                log_action("📜 Summary: Detailed", "summary_detailed", result)
                        if btn_cols_row1[2].button("Financial Focus"):
                            with st.spinner("Generating financial summary..."):
                                result = run_get_summary(st.session_state.document_text, st.session_state.doc_type, st.session_state.lang, "financial")
                                st.session_state.summary_result = result
                                log_action("📜 Summary: Financial", "summary_financial", result)

                        btn_cols_row2 = st.columns(3)
                        if btn_cols_row2[0].button("Executive Summary"):
                            with st.spinner("Generating executive summary..."):
                                result = run_get_summary(st.session_state.document_text, st.session_state.doc_type, st.session_state.lang, "executive")
                                st.session_state.summary_result = result
                                log_action("📜 Summary: Executive", "summary_executive", result)
                        if btn_cols_row2[1].button("Concise Summary"):
                            with st.spinner("Generating concise summary..."):
                                result = run_get_summary(st.session_state.document_text, st.session_state.doc_type, st.session_state.lang, "concise")
                                st.session_state.summary_result = result
                                log_action("📜 Summary: Concise", "summary_concise", result)
                    
                    if st.session_state.summary_result:
                        st.markdown("---")
                        st.markdown(st.session_state.summary_result)
            
            if "risk" in st.session_state.action_outputs:
                with st.container(border=True):
                    st.markdown("### Risk Assessment Dashboard")
                    try:
                        risk_data = json.loads(st.session_state.action_outputs["risk"])
                        if "error" in risk_data: raise ValueError(risk_data["error"])
                        details_text = risk_data.get("details", "No details provided.")
                        dash_cols = st.columns([1.5, 1, 1, 1])
                        with dash_cols[0]:
                            st.plotly_chart(create_risk_meter(risk_data.get("risk_score", 0), risk_data.get("risk_level", "N/A")), use_container_width=True)
                        with dash_cols[1]:
                            st.metric(label="Risk Score", value=f"{risk_data.get('risk_score', 0)}/100")
                        with dash_cols[2]:
                            st.metric(label="High-Risk Clauses", value=risk_data.get("high_risk_clauses", 0))
                        with dash_cols[3]:
                            st.metric(label="Medium-Risk Clauses", value=risk_data.get("medium_risk_clauses", 0))
                        with st.expander("See Detailed Risk Analysis and Mitigation Steps"):
                            st.markdown(details_text)
                    except Exception as e:
                        st.error(f"Could not generate risk dashboard. The AI response may not be in the correct format.", icon="⚠️")
                        with st.expander("Click to see the raw AI output for debugging"):
                            st.text(st.session_state.action_outputs["risk"])

            if "key_info" in st.session_state.action_outputs:
                with st.container(border=True):
                    st.markdown("### Key Information Hub")
                    try:
                        info_data = json.loads(st.session_state.action_outputs["key_info"])
                        if "error" in info_data: raise ValueError(info_data["error"])
                        valid_tabs = {k: v for k, v in info_data.items() if v}
                        if not valid_tabs:
                            st.info("No key information could be extracted for these categories.")
                        else:
                            tab_names = [key.replace('_', ' ').title() for key in valid_tabs.keys()]
                            tabs = st.tabs(tab_names)
                            for tab, (key, value) in zip(tabs, valid_tabs.items()):
                                with tab:
                                    if isinstance(value, dict) and value:
                                        for sub_key, sub_value in value.items():
                                            st.markdown(f"**{sub_key.replace('_', ' ').title()}:**")
                                            st.code(sub_value, language=None)
                                    elif isinstance(value, list) and value:
                                        st.markdown("\n".join(f"- {item}" for item in value))
                    except Exception as e:
                        st.error(f"Could not parse key info. The AI response may not be in the correct format.", icon="⚠️")
                        with st.expander("Click to see the raw AI output for debugging"):
                            st.text(st.session_state.action_outputs["key_info"])

            if "checklist" in st.session_state.action_outputs:
                with st.container(border=True):
                    st.markdown("### Compliance Scorecard")
                    try:
                        raw_output = st.session_state.action_outputs["checklist"]
                        checklist_data = json.loads(raw_output)
                        
                        if isinstance(checklist_data, dict) and "error" in checklist_data: 
                            raise ValueError(checklist_data["error"])
                        
                        if isinstance(checklist_data, dict): 
                            checklist_data = [checklist_data]

                        df = pd.DataFrame(checklist_data)
                        if 'status' not in df.columns: 
                            raise ValueError("Required 'status' column not found in the data.")
                        
                        status_counts = df['status'].value_counts()
                        chart_col, table_col = st.columns([1, 2])
                        with chart_col:
                            fig = px.pie(status_counts, values=status_counts.values, names=status_counts.index, title="Compliance Status", hole=0.5, color_discrete_map={'Pass':'green', 'Fail':'red', 'Review':'orange'})
                            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#FFFFFF') # <-- Text color fix
                            st.plotly_chart(fig, use_container_width=True)
                        with table_col:
                            st.dataframe(df, use_container_width=True, hide_index=True)
                    except Exception as e:
                        st.error(f"Could not generate compliance scorecard: {e}", icon="⚠️")
                        with st.expander("Click to see the raw AI output for debugging"):
                            st.text(st.session_state.action_outputs["checklist"])

            text_based_outputs = {"explain": "Complex Terms Explained", "simplify": "Simplified Document"}
            for key, title in text_based_outputs.items():
                if key in st.session_state.action_outputs:
                    with st.container(border=True):
                        st.markdown(f"### {title}")
                        st.markdown(st.session_state.action_outputs[key], unsafe_allow_html=True) 

    with sim_tab:
        st.subheader("₹ Cost Simulator")
        st.info("Estimate your out-of-pocket expenses based on your policy's rules.")
        
        if not st.session_state.get('financial_rules'):
            if st.button("Analyze Financial Rules for Simulation"):
                with st.spinner("Extracting policy rules (deductible, co-pay, etc.)..."):
                    try:
                        rules_json = ai_processor.extract_financial_rules(st.session_state.document_text, st.session_state.doc_type)
                        st.session_state.financial_rules = json.loads(rules_json)
                    except Exception as e:
                        st.error(f"Could not extract financial rules: {e}", icon="⚠️")
                        st.session_state.financial_rules = {"error": "Failed to parse AI response."}
                    st.rerun()
        else:
            rules = st.session_state.financial_rules
            if not rules or "error" in rules:
                st.error("Could not extract financial rules automatically. This feature may not be applicable to your document type or the AI failed to understand it.", icon="⚠️")
            else:
                st.success("Financial rules extracted successfully!")
                st.json(rules)
            
            with st.form("cost_calculator"):
                st.write("Enter your estimated medical costs (in ₹):")
                total_bill = st.number_input("Total Hospital Bill", min_value=0.0, step=100.0, format="%.2f")
                pharmacy_costs = st.number_input("Pharmacy & Medication Costs", min_value=0.0, step=10.0, format="%.2f")
                
                submitted = st.form_submit_button("Calculate My Cost")
                if submitted:
                    with st.spinner("Calculating liability based on your policy..."):
                        liability_json = None
                        try:
                            user_costs_str = json.dumps({"total_bill": total_bill, "pharmacy_costs": pharmacy_costs})
                            rules_str = json.dumps(rules if rules else {})
                            
                            liability_json = run_cost_calculation(rules_str, user_costs_str, st.session_state.doc_type)
                            liability_data = json.loads(liability_json)
                            
                            st.markdown("---")
                            st.subheader("Calculation Results")
                            res_col1, res_col2, res_col3 = st.columns(3)
                            
                            res_col1.metric("Total Bill", f"₹{liability_data.get('total_bill', 0):,.2f}")
                            res_col2.metric("Insurance Pays", f"₹{liability_data.get('insurance_pays', 0):,.2f}", delta_color="off")
                            res_col3.metric("You Pay (Out-of-Pocket)", f"₹{liability_data.get('user_pays', 0):,.2f}", delta_color="inverse")
                            
                            with st.expander("See Explanation"):
                                st.info(f"{liability_data.get('explanation', 'No explanation provided.')}")
                                
                            log_action("Cost Simulation", "cost_sim", liability_data)

                        except Exception as e:
                            st.error(f"Could not calculate costs: {e}", icon="⚠️")
                            if liability_json:
                                with st.expander("Click to see the raw AI output for debugging"):
                                    st.text(liability_json)
    
    with chat_tab:
        st.markdown("### Interactive Q&A Assistant")
        
        for entry in st.session_state.chat_history:
            with st.chat_message(entry["role"], avatar="👤" if entry["role"] == "user" else "🤖"):
                st.markdown(entry["content"])
                if entry["role"] == "ai" and entry.get("context"):
                    with st.expander("📚 View Source Context"):
                        st.info(entry["context"])
        
        if not st.session_state.chat_history:
            if st.session_state.suggested_questions and isinstance(st.session_state.suggested_questions, list):
                st.markdown("####  Suggested Questions")
                num_questions = len(st.session_state.suggested_questions)
                if num_questions > 0:
                    q_cols = st.columns(min(num_questions, 4)) 
                    for i, question in enumerate(st.session_state.suggested_questions[:4]):
                        if q_cols[i % len(q_cols)].button(f" {question}", key=f"suggestion_{i}", use_container_width=True):
                            st.session_state.user_input_from_button = question
                            st.rerun()

        prompt = st.chat_input("💭Type your question here...")
        if "user_input_from_button" in st.session_state:
            prompt = st.session_state.user_input_from_button
            del st.session_state["user_input_from_button"]

        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.spinner("Searching document for answer..."):
                chat_service.set_document_context(st.session_state.document_text, st.session_state.doc_type)
                response_dict = chat_service.ask_question(prompt, language=st.session_state.lang)
                ai_response = {
                    "role": "ai",
                    "content": response_dict.get("answer", "I apologize, but I encountered an error processing your question."),
                    "context": response_dict.get("context")
                }
                st.session_state.chat_history.append(ai_response)
                log_action("💬 AI Chat", "chat", {"question": prompt, "answer": ai_response["content"]})
            st.rerun()
            
        if len(st.session_state.chat_history) > 0:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Clear Chat History", use_container_width=True):
                    st.session_state.chat_history = []
                    if 'suggested_questions' in st.session_state:
                        with st.spinner("Generating new suggestions..."):
                            st.session_state.suggested_questions = run_question_generation(st.session_state.document_text, st.session_state.doc_type, st.session_state.lang)
                    st.rerun()

    with doc_tab:
        st.markdown("### Document Information")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Document Type:** {st.session_state.doc_type}")
        with col2:
            st.info(f"**Document Length:** {len(st.session_state.document_text):,} characters")
        
        st.markdown("### Extracted Text Preview")
        st.code(st.session_state.document_text[:Config.MAX_DOCUMENT_LENGTH // 2] + "\n\n... [Content continues]", language="text")


st.markdown("""
<div class="custom-footer">
    <p><strong>Healthcare Document AI Assistant</strong> | Powered by Advanced Generative AI | Secure & Confidential</p>
</div>
""", unsafe_allow_html=True)