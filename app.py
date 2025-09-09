import streamlit as st
from main import (
    extract_text_from_pdfs, ask_gemini, simplify_text, summarize_text, 
    translate_text, detect_document_type, extract_key_entities, 
    generate_compliance_checklist, explain_complex_terms, risk_assessment
)

# Page config with custom styling
st.set_page_config(
    page_title="Legal Document AI Assistant", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme-aware CSS
st.markdown("""
<style>
    :root {
        --primary-bg: var(--background-color);
        --primary-text: var(--text-color);
        --secondary-bg: #2d2d2d;
        --secondary-text: #f1f1f1;
    }

    /* Header */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Feature card */
    .feature-card {
        background: var(--primary-bg);
        color: var(--primary-text);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2a5298;
        margin: 1rem 0;
    }

    /* Doc type badge */
    .doc-type-badge {
        background: linear-gradient(45deg, #28a745, #20c997);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 1rem 0;
    }

    /* Chat messages */
    .chat-message {
        background: var(--secondary-bg);
        color: var(--secondary-text);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    /* Success box */
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%);
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Google AI badges */
    .google-badge {
        background: linear-gradient(45deg, #4285f4, #34a853, #fbbc05, #ea4335);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- UI Code (unchanged from your version) ---------------- #

# Enhanced Header
st.markdown("""
<div class="main-header">
    <h1>⚖️ AI-Powered Legal Document Assistant</h1>
    <p>🚀 Powered by Google's AI Ecosystem • Simplify • Translate • Analyze • Ask Questions</p>
</div>
""", unsafe_allow_html=True)

# Google AI Integration Showcase
st.markdown("""
<div style="text-align: center; margin: 1rem 0;">
    <span class="google-badge">🧠 Gemini 1.5 Flash</span>
    <span class="google-badge">👁️ Cloud Vision API</span>
    <span class="google-badge">🌍 Cloud Translate</span>
    <span class="google-badge">🔧 Google AI Studio</span>
</div>
""", unsafe_allow_html=True)

# ---------------- Your Existing Streamlit Logic ---------------- #
# (The rest of the file stays the same as in your uploaded app.py)


# How it Works Demo Section
with st.expander("🚀 Intelligent Document Analysis System", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        **📁 Smart Upload**
        - PDF text extraction
        - OCR for scanned docs
        - Multi-file processing
        """)
    with col2:
        st.markdown("""
        **🧠 AI Classification**
        - Auto-detect document type
        - Domain-specific analysis
        - Context-aware processing
        """)
    with col3:
        st.markdown("""
        **🔍 Intelligent Analysis**
        - Extract key entities
        - Risk assessment
        - Compliance checklists
        """)
    with col4:
        st.markdown("""
        **🌍 Multilingual**
        - Hindi & Kannada support
        - Regional accessibility
        - Cultural context
        """)

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("### 📂 Document Upload")
    
    uploaded_files = st.file_uploader(
        "Upload your documents here",
        type=["pdf"], 
        accept_multiple_files=True,
        help="📋 Supported: Legal contracts, Medical policies, Employment docs, Government forms"
    )
    
    if uploaded_files:
        st.markdown("### ✅ Uploaded Files")
        for i, file in enumerate(uploaded_files, 1):
            st.markdown(f"**{i}.** 📄 {file.name}")

    st.markdown("### 🌍 Language Preferences")
    language = st.selectbox(
        "Response Language:",
        ["English", "Hindi", "Kannada"],
        index=0,
        help="🗣️ All AI responses will be in your selected language"
    )

    st.markdown("### 🛠️ Quick Actions")
    if st.button("🧹 Clear All Data", type="secondary", use_container_width=True):
        for key in ['chat_history', 'pdf_text', 'doc_type', 'analysis_done']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Initialize session state
for key in ['pdf_text', 'chat_history', 'doc_type', 'analysis_done']:
    if key not in st.session_state:
        if key == 'chat_history':
            st.session_state[key] = []
        elif key == 'analysis_done':
            st.session_state[key] = False
        else:
            st.session_state[key] = ""

# Welcome screen for new users
if not uploaded_files:
    st.markdown("""
    <div class="feature-card">
        <h3>🎯 What makes this assistant special?</h3>
        <ul style="font-size: 1.1rem; line-height: 1.6;">
            <li><strong>🧠 Smart Document Understanding:</strong> Automatically detects and analyzes different document types</li>
            <li><strong>🔍 Domain Expertise:</strong> Specialized knowledge for legal contracts, medical policies, and employment documents</li>
            <li><strong>⚡ Google AI Integration:</strong> Powered by Gemini, Cloud Vision, and Translate APIs</li>
            <li><strong>🌍 Accessibility Focus:</strong> Hindi and Kannada language support for regional users</li>
            <li><strong>📋 Actionable Insights:</strong> Risk assessments, compliance checklists, and practical guidance</li>
            <li><strong>🔒 Comprehensive Analysis:</strong> Extract key entities, explain complex terms, identify potential issues</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("👆 **Get Started:** Upload your legal or medical documents using the sidebar!")

# Document Processing Pipeline
if uploaded_files and not st.session_state.pdf_text:
    with st.spinner("🔄 Processing documents with Google AI..."):
        progress_bar = st.progress(0)
        st.write("📄 Extracting text from documents...")
        progress_bar.progress(33)
        
        st.session_state.pdf_text = extract_text_from_pdfs(uploaded_files)
        progress_bar.progress(66)
        
        st.write("🧠 Analyzing document type...")
        st.session_state.doc_type = detect_document_type(st.session_state.pdf_text)
        progress_bar.progress(100)
    
    st.markdown("""
    <div class="success-box">
        ✅ <strong>Document processing complete!</strong> Ready for intelligent analysis.
    </div>
    """, unsafe_allow_html=True)
    
    st.balloons()  # Celebration effect

# Document Type Display & Smart Analysis
if st.session_state.pdf_text and st.session_state.doc_type:
    # Document type badge
    st.markdown(f"""
    <div class="doc-type-badge">
        📋 Document Type: {st.session_state.doc_type}
    </div>
    """, unsafe_allow_html=True)
    
    # Smart Analysis Section
    st.markdown("### 🧠 Intelligent Document Analysis")
    st.markdown("*Powered by domain-specific AI expertise*")
    
    # Analysis buttons in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔑 Extract Key Information", use_container_width=True):
            with st.spinner("🔍 Analyzing key entities with domain expertise..."):
                key_info = extract_key_entities(st.session_state.pdf_text, st.session_state.doc_type)
                if language != "English":
                    key_info = translate_text(key_info, language)
                st.session_state.chat_history.append((f"🔑 Key Information Analysis ({st.session_state.doc_type})", key_info))
            st.success("✅ Key information extracted!")

    with col2:
        if st.button("📝 Generate Action Checklist", use_container_width=True):
            with st.spinner("📋 Creating personalized compliance checklist..."):
                checklist = generate_compliance_checklist(st.session_state.pdf_text, st.session_state.doc_type)
                if language != "English":
                    checklist = translate_text(checklist, language)
                st.session_state.chat_history.append((f"📝 Action Checklist ({st.session_state.doc_type})", checklist))
            st.success("✅ Checklist generated!")

    with col3:
        if st.button("⚠️ Risk Assessment", use_container_width=True):
            with st.spinner("⚖️ Analyzing potential risks and concerns..."):
                risks = risk_assessment(st.session_state.pdf_text, st.session_state.doc_type)
                if language != "English":
                    risks = translate_text(risks, language)
                st.session_state.chat_history.append((f"⚠️ Risk Assessment ({st.session_state.doc_type})", risks))
            st.success("✅ Risk assessment complete!")

    # Additional analysis tools
    col4, col5 = st.columns(2)
    
    with col4:
        if st.button("📖 Explain Complex Terms", use_container_width=True):
            with st.spinner("📚 Identifying and explaining complex terminology..."):
                terms = explain_complex_terms(st.session_state.pdf_text, st.session_state.doc_type)
                if language != "English":
                    terms = translate_text(terms, language)
                st.session_state.chat_history.append((f"📖 Complex Terms Explained ({st.session_state.doc_type})", terms))
            st.success("✅ Terms explained!")

    with col5:
        if st.button("📄 Comprehensive Summary", use_container_width=True):
            with st.spinner("📊 Creating detailed document summary..."):
                summary = summarize_text(st.session_state.pdf_text, st.session_state.doc_type)
                if language != "English":
                    summary = translate_text(summary, language)
                st.session_state.chat_history.append((f"📄 Document Summary ({st.session_state.doc_type})", summary))
            st.success("✅ Summary generated!")

    # Preview section
    with st.expander("👀 Preview Extracted Content", expanded=False):
        preview_text = st.session_state.pdf_text[:2000]
        if len(st.session_state.pdf_text) > 2000:
            preview_text += "\n\n... (content truncated for preview)"
        st.text_area("Extracted Text", preview_text, height=300, disabled=True)

# Enhanced Q&A Section
if st.session_state.pdf_text:
    st.markdown("### 🔍 Interactive Q&A with Domain Expertise")
    st.markdown("*Ask questions and get expert-level analysis*")

    # Smart questions based on document type
    if st.session_state.doc_type:
        smart_questions = {
            "Legal Contract": [
                "What are my main obligations under this contract?",
                "What happens if I want to terminate this agreement?",
                "Are there any penalties or fees I should know about?",
                "What are the payment terms and due dates?"
            ],
            "Medical Policy": [
                "What medical services are covered by this policy?",
                "How much will I typically pay out of pocket?",
                "What's the process for filing insurance claims?",
                "Which doctors and hospitals can I use?"
            ],
            "Medical Report": [
                "What do my test results indicate?",
                "What medications should I take and when?",
                "What symptoms should I watch out for?",
                "When do I need follow-up appointments?"
            ],
            "Employment Document": [
                "What are my key job responsibilities?",
                "What benefits am I entitled to?",
                "What's the performance review process?",
                "What are the terms for resignation or termination?"
            ]
        }
        
        # Get relevant questions for this document type
        doc_type_key = next((key for key in smart_questions.keys() if key in st.session_state.doc_type), "Legal Contract")
        relevant_questions = smart_questions[doc_type_key]
        
        st.markdown(f"**💡 Expert questions for {st.session_state.doc_type}:**")
        cols = st.columns(2)
        for i, question in enumerate(relevant_questions):
            with cols[i % 2]:
                if st.button(f"❓ {question}", key=f"expert_q_{i}"):
                    with st.spinner("🧠 Analyzing with domain expertise..."):
                        answer = ask_gemini(question, st.session_state.pdf_text, language, st.session_state.doc_type)
                    st.session_state.chat_history.append((question, answer))

    # Custom question form
    st.markdown("**🎯 Ask your own questions:**")
    with st.form("qa_form", clear_on_submit=True):
        user_question = st.text_input(
            "Your question:", 
            placeholder="e.g., What should I be most careful about in this document?",
            help="💬 Ask anything about your document - the AI has domain-specific expertise!"
        )
        submitted = st.form_submit_button("🚀 Get Expert Analysis", use_container_width=True)

    if submitted:
        if not user_question.strip():
            st.warning("⚠️ Please enter your question.")
        else:
            with st.spinner(f"🤖 Analyzing your question with {language} expertise..."):
                answer = ask_gemini(user_question, st.session_state.pdf_text, language, st.session_state.doc_type)
            st.session_state.chat_history.append((user_question, answer))

# Conversation History Display
if st.session_state.chat_history:
    st.markdown("### 💬 Analysis Results & Conversation History")
    
    for i, (question, answer) in enumerate(reversed(st.session_state.chat_history)):
        with st.container():
            # Question
            st.markdown(f"**❓ {question}**")
            
            # Answer with formatting
            st.markdown(f"""
            <div class="chat-message">
                <strong>🤖 AI Analysis ({language}):</strong><br>
                {answer.replace('**', '<strong>').replace('**', '</strong>').replace('\n', '<br>')}
            </div>
            """, unsafe_allow_html=True)
            
            # Add separator except for last item
            if i < len(st.session_state.chat_history) - 1:
                st.markdown("---")

# Statistics and Analytics
if st.session_state.pdf_text:
    with st.expander("📊 Document Analytics", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Documents", len(uploaded_files) if uploaded_files else 0)
        with col2:
            st.metric("📝 Total Words", len(st.session_state.pdf_text.split()))
        with col3:
            st.metric("💬 Questions Asked", len(st.session_state.chat_history))
        with col4:
            st.metric("🧠 Document Type", st.session_state.doc_type.split('/')[0] if st.session_state.doc_type else "Unknown")

# Footer with enhanced branding
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px; margin: 2rem 0;'>
    <h4 style='color: #2a5298; margin-bottom: 1rem;'>🚀 Built for Google AI Hackathon</h4>
    <p style='color: #666; margin-bottom: 1rem;'>
        <strong>Making Legal Documents Accessible for Everyone</strong><br>
        Powered entirely by Google's AI Ecosystem • Domain-Specific Intelligence • Multilingual Support
    </p>
    <div style='margin-top: 1rem;'>
        <span class="google-badge">⚖️ Legal AI</span>
        <span class="google-badge">🏥 Medical AI</span>
        <span class="google-badge">🌍 Multilingual</span>
        <span class="google-badge">🔒 Privacy First</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Technical Details Expander for Judges
with st.expander("🔧 Technical Architecture (For Judges)", expanded=False):
    st.markdown("""
    ### 🏗️ Google AI Ecosystem Integration
    
    **Core AI Engine:**
    - **Google Gemini 1.5 Flash**: Advanced document analysis and natural language processing
    - **Context Window**: Up to 15K tokens for comprehensive document understanding
    - **Domain-Specific Prompting**: Custom prompt engineering for legal/medical document types
    
    **Intelligent Document Processing:**
    - **Google Cloud Vision API**: OCR fallback for scanned/image-based documents
    - **Automatic Document Classification**: AI-powered detection of document types
    - **Entity Extraction**: Domain-specific key information identification
    
    **Multilingual Capabilities:**
    - **Google Cloud Translate API**: Professional-grade translation services
    - **Gemini Translation Fallback**: AI-powered translation when Cloud Translate unavailable
    - **Cultural Context Preservation**: Maintains meaning across languages
    
    **Advanced Features:**
    - **Risk Assessment Engine**: Identifies potential legal/medical concerns
    - **Compliance Checklist Generation**: Automated actionable item creation
    - **Complex Term Explanation**: Jargon simplification for accessibility
    - **Interactive Q&A**: Context-aware question answering with domain expertise
    
    ### 🧠 Why This Isn't Just a "Wrapper"
    
    **Intelligent Orchestration:**
    - Multi-step document processing pipeline
    - Document type detection drives specialized analysis
    - Context-aware prompt engineering based on domain
    - Error handling and graceful fallbacks
    
    **Value-Added Intelligence:**
    - Domain-specific entity extraction
    - Risk assessment algorithms
    - Automated compliance checklist generation
    - Complex term identification and explanation
    
    **Complete User Experience:**
    - File upload and processing management
    - Conversation history and state management
    - Progress tracking and user feedback
    - Multilingual user interface
    
    **Google AI Best Practices:**
    - Responsible AI usage with appropriate disclaimers
    - Privacy-conscious design (no data storage)
    - Efficient token usage and cost optimization
    - Scalable architecture using Google Cloud services
    """)

# Developer Notes (Hidden by default)
if st.checkbox("🔍 Show Developer Debug Info", key="debug_mode"):
    st.markdown("### 🛠️ Debug Information")
    st.write("**Session State:**")
    debug_state = {k: str(v)[:100] + "..." if len(str(v)) > 100 else v 
                   for k, v in st.session_state.items() 
                   if k != 'pdf_text'}  # Don't show full text
    st.json(debug_state)
    
    if st.session_state.pdf_text:
        st.write(f"**Document Length:** {len(st.session_state.pdf_text)} characters")
        st.write(f"**Word Count:** {len(st.session_state.pdf_text.split())} words")