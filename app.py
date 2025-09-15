import streamlit as st
from pathlib import Path
from main import extract_text_from_files as extract_text_from_pdfs

# Assuming these functions are available in your main.py.
from main import (
    detect_document_type,
    extract_key_entities,
    generate_compliance_checklist,
    explain_complex_terms,
    risk_assessment,
    ask_gemini,
    simplify_text,
    summarize_text,
    translate_text, # Although not explicitly used in app.py logic, it's imported
)

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(
    page_title="AI Legal Document Assistant",
    page_icon="⚖️",
    layout="wide"
)

# -------------------------------
# Custom CSS for a modern, vibrant dark theme UI
# New color palette:
# Backgrounds: Deep space blues/purples
# Primary Accent: Vibrant Teal/Aqua
# Secondary Accent: Electric Purple
# Text: Soft whites
# -------------------------------
st.markdown("""<style>
/* Global styles */
html, body, .main, .block-container {
    background-color: #1A1A2E; /* Deep space blue/purple */
    color: #E0E0F0; /* Soft off-white for primary text */
    font-family: 'Inter', sans-serif; /* Modern, clean font */
    line-height: 1.6;
    scroll-behavior: smooth;
}
p { margin-bottom: 1em; }
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF; /* Pure white for headers */
    font-weight: 700;
    margin-top: 1.8em;
    margin-bottom: 0.8em;
    letter-spacing: 0.5px;
}
strong { color: #FFFFFF; } /* Ensure bold text stands out */

/* Sidebar styling - now we're explicitly hiding it if not used */
[data-testid="stSidebar"] {
    display: none; /* Hide the sidebar completely */
}

/* File Uploader styling */
div[data-testid="stFileUploader"] {
    border: 2px dashed #00B4D8; /* Vibrant blue accent for dashed border */
    border-radius: 12px;
    background: #2A2A47; /* Darker background for uploader area */
    padding: 25px;
    margin-top: 25px;
    margin-bottom: 35px;
    transition: all 0.3s ease-in-out;
    text-align: center;
    min-height: 200px; /* Give it more presence */
    display: flex; /* Flexbox for centering content */
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
div[data-testid="stFileUploader"]:hover {
    border-color: #6A05AD; /* Electric purple on hover */
    background: #303050;
    box-shadow: 0 0 15px rgba(0, 180, 216, 0.3);
}
.stFileUploader label {
    color: #E0E0F0;
    font-weight: 600;
    font-size: 1.1em;
    margin-bottom: 15px;
    display: block;
}
/* Specific targeting for the "Drag and drop files here" text */
div[data-testid="stFileUploader"] .st-emotion-cache-1wmy9hp p {
    color: #A0A0B5; /* Muted text for drag instructions */
    font-size: 1.1em;
    font-weight: 400;
    margin-bottom: 0; /* Remove default paragraph margin */
}
/* Specific targeting for the "Limit 200MB per file • PDF" text */
div[data-testid="stFileUploader"] .st-emotion-cache-1wmy9hp > div:last-of-type {
    color: #70708A; /* Even more muted */
    font-size: 0.9em;
    margin-top: 5px; /* Add some space from the drag text */
}

.stFileUploader button {
    background: linear-gradient(90deg, #6A05AD, #00B4D8) !important; /* Gradient for browse button */
    border: none !important;
    color: white !important;
    padding: 10px 25px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    margin-top: 15px;
    transition: all 0.3s ease-in-out;
}
.stFileUploader button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 4px 15px rgba(106, 5, 173, 0.4) !important;
}

/* New CSS for displaying uploaded file items */
div[data-testid="stFileUploadProgress"] {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #353550; /* Darker background for the file item */
    border-radius: 8px;
    padding: 10px 15px;
    margin-top: 15px; /* Space between files if multiple */
    box-shadow: 0px 2px 8px rgba(0,0,0,0.3);
    border: 1px solid #454560;
}

div[data-testid="stFileUploadProgress"] div:first-child { /* Container for icon, name, size */
    display: flex;
    align-items: center;
    gap: 10px;
    color: #E0E0F0;
    font-size: 1em;
}

div[data-testid="stFileUploadProgress"] svg { /* Icon */
    color: #00B4D8; /* Vibrant blue for the document icon */
    font-size: 1.2em;
}

div[data-testid="stFileUploadProgress"] span { /* File name and size text */
    color: #E0E0F0;
}

button[data-testid="stFileUploaderClearButton"] {
    background: linear-gradient(90deg, #6A05AD, #00B4D8) !important; /* Gradient for close button */
    border: none !important;
    color: white !important;
    border-radius: 50% !important; /* Circular button */
    width: 30px !important;
    height: 30px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.2em !important;
    padding: 0 !important;
    margin: 0 !important;
    transition: all 0.2s ease-in-out;
}

button[data-testid="stFileUploaderClearButton"]:hover {
    transform: scale(1.1);
    box-shadow: 0px 0px 10px rgba(106, 5, 173, 0.6) !important;
}


/* Header styling */
.app-header {
    text-align: center;
    padding: 30px 0;
    background: linear-gradient(90deg, #6A05AD, #00B4D8); /* Electric purple to vibrant blue gradient */
    border-radius: 18px; /* More rounded corners */
    color: white;
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 50px;
    letter-spacing: 1.5px;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.5); /* Stronger, deeper shadow */
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
}
.app-header svg {
    font-size: 40px;
}

/* Button styling */
.stButton>button {
    border-radius: 10px;
    background: linear-gradient(90deg, #6A05AD, #00B4D8);
    color: white;
    border: none;
    padding: 0.9em 2em;
    font-weight: 600;
    transition: all 0.3s ease-in-out;
    letter-spacing: 0.7px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    font-size: 1.1em;
    margin-top: 15px;
    margin-bottom: 15px;
}
.stButton>button:hover {
    transform: translateY(-5px); /* More dynamic lift */
    box-shadow: 0px 10px 25px rgba(106, 5, 173, 0.5); /* Enhanced hover shadow */
    cursor: pointer;
}
.stButton > button:disabled {
    background: #3A3A5E; /* Muted dark blue for disabled */
    color: #A0A0B5;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
    opacity: 0.7;
}

/* Chat bubble styling */
.chat-bubble-user {
    background: #00B4D8; /* User message vibrant blue */
    color: white;
    padding: 16px 22px;
    border-radius: 28px 28px 10px 28px; /* Organic, modern shape */
    margin: 12px 0;
    max-width: 70%;
    align-self: flex-end;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.25);
    margin-left: auto;
    text-align: left;
    font-size: 1.05em;
}
.chat-bubble-ai {
    background: #2A2A47; /* AI message dark background */
    color: #E0E0F0;
    padding: 16px 22px;
    border-radius: 28px 28px 28px 10px; /* Organic, modern shape */
    margin: 12px 0;
    max-width: 70%;
    align-self: flex-start;
    border: 1px solid #353550;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.15);
    margin-right: auto;
    text-align: left;
    font-size: 1.05em;
}
div.stChatMessage {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

/* Tabs styling */
.stTabs [data-testid="stTabContent"] {
    padding: 2.5rem 0;
}
.stTabs [data-testid="stTab"] {
    background-color: #2A2A47; /* Dark background for inactive tabs */
    color: #A0A0B5; /* Muted color for inactive tab text */
    border-radius: 15px 15px 0 0; /* More rounded top corners */
    margin-right: 12px;
    padding: 18px 35px; /* Larger tabs for better click area */
    border: 1px solid #353550;
    border-bottom: none;
    transition: all 0.3s ease-in-out;
    font-weight: 600;
    font-size: 1.15em;
    letter-spacing: 0.3px;
}
.stTabs [data-testid="stTab"]:hover {
    background-color: #303050;
    color: #E0E0F0;
    cursor: pointer;
}
.stTabs [data-testid="stTab"][aria-selected="true"] {
    background-color: #00B4D8; /* Primary accent color for selected tab */
    color: white;
    border: 1px solid #00B4D8;
    font-weight: 700;
    box-shadow: 0px -5px 15px rgba(0, 180, 216, 0.4);
    position: relative;
    z-index: 1;
}

/* Input Fields (Selectbox, Text Input) styling */
div[data-testid="stSelectbox"] > label,
div[data-testid="stTextInput"] label {
    color: #E0E0F0;
    font-weight: 600;
    margin-bottom: 10px;
    font-size: 1.1em;
}

/* Specific styling for selectbox widget */
div[data-testid="stSelectbox"] div.st-emotion-cache-1wv8cff,
div[data-testid="stSelectbox"] div.st-emotion-cache-1wv8cff > div { /* Target the actual select box wrapper */
    background-color: #2A2A47;
    border: 1px solid #353550;
    border-radius: 8px;
    color: #E0E0F0;
    padding: 0.7em 1.3em;
    transition: all 0.3s ease-in-out;
}
div[data-testid="stSelectbox"] div.st-emotion-cache-1wv8cff:hover {
    border-color: #00B4D8;
    box-shadow: 0 0 0 0.15rem rgba(0, 180, 216, 0.25);
}
div[data-testid="stSelectbox"] .st-emotion-cache-1wv8cff > div > span {
    color: #E0E0F0;
}
/* Dropdown arrow */
div[data-testid="stSelectbox"] .st-emotion-cache-ch5d6d {
    color: #6A05AD; /* Electric purple arrow */
}


/* Specific styling for text input fields */
div[data-testid="stTextInput"] div.st-emotion-cache-1c7y2k2,
div[data-testid="stTextInput"] div.st-emotion-cache-h5rpjc {
    background-color: #2A2A47;
    border: 1px solid #353550;
    border-radius: 10px;
    color: #E0E0F0;
    padding: 0.7em 1.2em;
    transition: all 0.3s ease-in-out;
}
div[data-testid="stTextInput"] textarea,
div[data-testid="stTextInput"] input {
    background-color: #2A2A47;
    color: #E0E0F0;
    border: none;
    font-size: 1.05em;
}
div[data-testid="stTextInput"] div.st-emotion-cache-1c7y2k2:focus-within,
div[data-testid="stTextInput"] div.st-emotion-cache-h5rpjc:focus-within {
    border-color: #00B4D8;
    box-shadow: 0 0 0 0.2rem rgba(0, 180, 216, 0.35);
}

/* Status messages (success, info, warning, error) */
.stAlert {
    border-radius: 10px;
    padding: 20px 25px;
    margin-bottom: 25px;
    font-size: 1.05em;
    line-height: 1.5;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.2);
}
.stAlert.success {
    background-color: #284A4A; /* Dark green-blue */
    color: #64FFDA; /* Vibrant light green */
    border-left: 6px solid #1DE9B6;
}
.stAlert.info {
    background-color: #2A444D; /* Darker blue */
    color: #80ED99; /* Light green-blue */
    border-left: 6px solid #00B4D8;
}
.stAlert.warning {
    background-color: #4A402A; /* Dark yellow-brown */
    color: #FFDA64; /* Vibrant yellow */
    border-left: 6px solid #FFC107;
}
.stAlert.error {
    background-color: #4A2A2A; /* Dark red */
    color: #FF8A80; /* Light red */
    border-left: 6px solid #EF5350;
}

/* Spinner styling */
.stSpinner > div {
    color: #00B4D8; /* Primary accent color for spinner animation */
}
.stSpinner > div > div {
    color: #E0E0F0;
    font-size: 1.15em;
}

/* Code block styling */
div.stCodeBlock {
    background-color: #2A2A47;
    border: 1px solid #353550;
    border-radius: 10px;
    padding: 20px;
    margin-top: 25px;
    margin-bottom: 25px;
    overflow-x: auto;
    font-size: 0.95em;
    line-height: 1.4;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.15);
}
pre {
    background-color: #2A2A47 !important;
    color: #E0E0F0 !important;
    border: none !important;
}

/* Footer (for copyright) */
.footer {
    width: 100%;
    text-align: center;
    padding: 35px 20px;
    color: #A0A0B5; /* Muted color for footer text */
    font-size: 14px;
    margin-top: 70px;
    border-top: 1px solid #353550;
    background-color: #202038;
    border-radius: 0 0 15px 15px; /* Match header curvature if possible */
    box-shadow: 0px -5px 15px rgba(0,0,0,0.3);
}

/* Scrollbar styling */
::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-track { background: #2A2A47; border-radius: 10px; }
::-webkit-scrollbar-thumb { background: #00B4D8; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #6A05AD; }

</style>""", unsafe_allow_html=True)

# Initialize session state for chat history if not already present
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize session state for action outputs if not already present
if 'action_outputs' not in st.session_state:
    st.session_state.action_outputs = {}

# Initialize session state for document processing status and data
if 'document_processed' not in st.session_state:
    st.session_state.document_processed = False
if 'document_text' not in st.session_state:
    st.session_state.document_text = None
if 'doc_type' not in st.session_state:
    st.session_state.doc_type = "Unknown"
if 'lang' not in st.session_state: # Default language
    st.session_state.lang = "English"

# --- Function to reset the application state ---
def reset_app_state():
    st.session_state.document_processed = False
    st.session_state.document_text = None
    st.session_state.doc_type = "Unknown"
    st.session_state.chat_history = []
    st.session_state.action_outputs = {}
    st.session_state.uploaded_files_key = st.session_state.get('uploaded_files_key', 0) + 1 # Increment key to ensure uploader resets
    # REMOVED: st.rerun() here. The script will naturally rerun after this callback finishes.


# -------------------------------
# Header
# -------------------------------
st.markdown('<div class="app-header">⚖️ AI-Powered Legal Document Assistant</div>', unsafe_allow_html=True)

# --- Conditional Rendering of Initial Upload vs. Document Interaction ---
if not st.session_state.document_processed:
    # Initial "Get Started" screen
    st.markdown("<h2 style='text-align: center; color: #E0E0F0; margin-bottom: 2em;'>Get Started: Upload Your Legal Document(s)</h2>", unsafe_allow_html=True)

    # Use a central column for better organization and centering
    _, center_col, _ = st.columns([1, 3, 1])

    with center_col:
        # Upload PDF(s) section (placed first, and centered within center_col)
        st.markdown("### <div style='text-align: center; margin-bottom: 1em;'>📂 Upload PDF(s)</div>", unsafe_allow_html=True)
        
        # We need a dynamic key for the file uploader to force a reset when needed
        if 'uploaded_files_key' not in st.session_state:
            st.session_state.uploaded_files_key = 0
        
        uploaded_files = st.file_uploader(
            "Drag and drop your PDF(s), JPEGs, or PNGs here",
            type=["pdf", "jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key=f"file_uploader_initial_{st.session_state.uploaded_files_key}", # Dynamic key
            label_visibility="collapsed" # Hide the default Streamlit label
        )

        # Language selector section (placed below uploader, and centered within center_col)
        st.markdown("---") # Visual separator
        st.markdown("### <div style='text-align: center; margin-bottom: 0.5em;'>🌐 Answer Language</div>", unsafe_allow_html=True)
        # To make the selectbox appear more centrally aligned if it doesn't take full width
        lang_col_left, lang_col_center_inner, lang_col_right = st.columns([0.5, 2, 0.5]) # Nested columns for selectbox
        with lang_col_center_inner:
            st.session_state.lang = st.selectbox(
                "Select Language for AI Responses",
                ["English", "Hindi", "Kannada"],
                key="lang_select_initial",
                label_visibility="collapsed",
                index=["English", "Hindi", "Kannada"].index(st.session_state.lang) if st.session_state.lang in ["English", "Hindi", "Kannada"] else 0
            )
        
        # General guidance message below both elements
        st.markdown(
            "<p style='text-align: center; margin-top: 2em; color: #A0A0B5; font-size: 1.1em;'>"
            "Upload <strong>one or more</strong> legal documents (PDF, JPEG, or PNG) above. "
            "Our AI will extract and <strong>combine their content for comprehensive analysis</strong> and interaction."
            "</p>", unsafe_allow_html=True
        )

    # Processing logic for uploaded files
    if uploaded_files:
        num_files = len(uploaded_files)
        if num_files == 1:
            st.success("1 file uploaded successfully! Processing...")
        else:
            st.success(f"{num_files} files uploaded successfully! Text extracted and combined for processing...")
            
        with st.spinner("🔍 Extracting text from PDFs..."):
            document_text = extract_text_from_pdfs(uploaded_files)
        
        if document_text:
            doc_type = detect_document_type(document_text)
            st.session_state.document_text = document_text
            st.session_state.doc_type = doc_type
            st.session_state.document_processed = True
            st.rerun() # Rerun to switch to the document interaction view
        else:
            st.error("❌ Could not extract any text from the uploaded files. Please try again.")
            # Keep document_processed as False if extraction fails, so the upload UI remains

else:
    # Document has been processed, show interaction tabs
    document_text = st.session_state.document_text
    doc_type = st.session_state.doc_type
    
    # Header with Language Selector and "Upload New Document" Button
    header_col_left, header_col_lang, header_col_reset = st.columns([2, 1, 1])
    
    with header_col_lang:
        st.markdown("<span style='color: #E0E0F0; margin-right: 10px; font-weight: 600;'>🌐 Language:</span>", unsafe_allow_html=True)
        st.session_state.lang = st.selectbox(
            "Answer Language",
            ["English", "Hindi", "Kannada"],
            key="lang_select_persistent",
            label_visibility="collapsed",
            index=["English", "Hindi", "Kannada"].index(st.session_state.lang) if st.session_state.lang in ["English", "Hindi", "Kannada"] else 0
        )
    with header_col_reset:
        if st.button("🔄 Start Over / Upload New Document", on_click=reset_app_state, use_container_width=True, key="btn_new_document"):
            # This info message will appear on the *new* upload page after the rerun
            st.info("Application state reset. Please upload a new document to begin again.")
            # No explicit rerun here, as the on_click callback already triggers a rerun for the state changes.
    
    st.markdown("---") # Separator below the language selector and reset button
    st.subheader("Document Interaction & AI Assistant")

    tab1, tab2, tab3 = st.tabs(["📑 Document View", "⚡ Actions", "💬 Ask AI"])

    with tab1:
        st.write(f"**Detected Document Type (overall):** <span style='color:#00B4D8;'>{doc_type}</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.info("Below is the **combined extracted text** from all your uploaded document(s). A truncated version is displayed for preview. The full combined text is utilized for all AI processing in the 'Actions' and 'Ask AI' tabs.")
        st.code(document_text[:2000] + "...\n\n[Truncated for preview. Full text is available for processing.]", language="text")

    with tab2:
        st.write(f"**Document Type (overall):** <span style='color:#00B4D8;'>{doc_type}</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.write("Perform various AI-powered actions on your uploaded document:")
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📌 Extract Key Information", use_container_width=True, key="btn_key_info"):
                with st.spinner("Extracting key entities..."):
                    result = extract_key_entities(document_text, doc_type, st.session_state.lang)
                    st.session_state.action_outputs["key_info"] = {"type": "success", "header": "Key Information Extracted Successfully!", "content": result}
                st.rerun()

            if st.button("⚠️ Risk Assessment", use_container_width=True, key="btn_risk_assessment"):
                with st.spinner("Performing risk assessment..."):
                    result = risk_assessment(document_text, doc_type, st.session_state.lang)
                    st.session_state.action_outputs["risk_assessment"] = {"type": "warning", "header": "Risk Assessment Complete:", "content": result}
                st.rerun()

            if st.button("📚 Explain Complex Terms", use_container_width=True, key="btn_explain_terms"):
                with st.spinner("Explaining complex terms..."):
                    result = explain_complex_terms(document_text, doc_type, st.session_state.lang)
                    st.session_state.action_outputs["explain_terms"] = {"type": "info", "header": "Complex Terms Explained:", "content": result}
                st.rerun()

        with col2:
            if st.button("📝 Generate Compliance Checklist", use_container_width=True, key="btn_checklist"):
                with st.spinner("Generating compliance checklist..."):
                    result = generate_compliance_checklist(document_text, doc_type, st.session_state.lang)
                    st.session_state.action_outputs["compliance_checklist"] = {"type": "success", "header": "Compliance Checklist Generated:", "content": result}
                st.rerun()

            if st.button("📖 Summarize Document", use_container_width=True, key="btn_summarize"):
                with st.spinner("Summarizing document..."):
                    result = summarize_text(document_text, doc_type, st.session_state.lang)
                    st.session_state.action_outputs["summarize_document"] = {"type": "success", "header": "Document Summarized:", "content": result}
                st.rerun()

            if st.button("🔄 Simplify Document", use_container_width=True, key="btn_simplify"):
                with st.spinner("Simplifying text..."):
                    result = simplify_text(document_text, doc_type, st.session_state.lang)
                    st.session_state.action_outputs["simplify_document"] = {"type": "info", "header": "Document Simplified (Plain Language):", "content": result}
                st.rerun()
        
        if st.session_state.action_outputs:
            st.markdown("---")
            st.subheader("Results:")
            for key, output in st.session_state.action_outputs.items():
                if output["type"] == "success":
                    st.success(output["header"])
                elif output["type"] == "warning":
                    st.warning(output["header"])
                elif output["type"] == "info":
                    st.info(output["header"])
                st.markdown(output["content"])
                st.markdown("---")

    with tab3:
        st.markdown("---")
        st.write("Ask questions about your document using our AI Assistant:")
        st.markdown("---")

        for entry in st.session_state.chat_history:
            if entry["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user">{entry["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai">{entry["content"]}</div>', unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        user_input = st.text_input("Type your question...", key="chat_input", placeholder="e.g., What are the key responsibilities of Party A?")
        
        col_ask, _ = st.columns([0.2, 0.8])
        with col_ask:
            if st.button("Ask", key="ask_button", use_container_width=True):
                if user_input:
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    
                    with st.spinner("🤖 Processing your query..."):
                        response = ask_gemini(user_input, document_text, language=st.session_state.lang, doc_type=doc_type)
                        st.session_state.chat_history.append({"role": "ai", "content": response})
                    st.rerun()
                else:
                    st.warning("Please type a question to ask.")


# -------------------------------
# Footer (Copyright)
# -------------------------------
st.markdown("""
<div class="footer">
    AI Legal Document Assistant.
</div>
""", unsafe_allow_html=True)