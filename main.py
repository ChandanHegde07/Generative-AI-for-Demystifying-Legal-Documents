import os
from dotenv import load_dotenv
import google.generativeai as genai
from pypdf import PdfReader

# Optional OCR + Translation
try:
    from google.cloud import vision
    from google.cloud import translate_v2 as translate
    OCR_ENABLED = True
except ImportError:
    OCR_ENABLED = False

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("Google API key not found. Please set it in your .env file as GOOGLE_API_KEY.")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ----------------- Document Extraction -----------------
def extract_text_from_files(uploaded_files) -> str:
    """
    Extract text from multiple PDF/image files.
    - Uses PyPDF for PDFs
    - Falls back to OCR if needed
    - Direct OCR for JPG/PNG images
    Returns merged text from all files
    """
    all_text = ""

    for file in uploaded_files:
        text = ""

        # ---------- PDF Handling ----------
        if file.name.lower().endswith(".pdf"):
            try:
                reader = PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() or ""
            except Exception:
                pass

            # Fallback OCR if empty
            if OCR_ENABLED and not text.strip():
                try:
                    file.seek(0)
                    client = vision.ImageAnnotatorClient()
                    content = file.read()
                    image = vision.Image(content=content)
                    response = client.document_text_detection(image=image)
                    text = response.full_text_annotation.text if response.text_annotations else ""
                except Exception as e:
                    text = f"[OCR failed: {e}]"

        # ---------- Image Handling ----------
        elif file.name.lower().endswith((".jpg", ".jpeg", ".png")) and OCR_ENABLED:
            try:
                file.seek(0)
                client = vision.ImageAnnotatorClient()
                content = file.read()
                image = vision.Image(content=content)
                response = client.document_text_detection(image=image)
                text = response.full_text_annotation.text if response.text_annotations else ""
            except Exception as e:
                text = f"[Image OCR failed: {e}]"

        all_text += text.strip() + "\n\n--- End of Document ---\n\n"

    return all_text.strip()


# ----------------- Domain-Specific Intelligence -----------------
def detect_document_type(text: str) -> str:
    """Detect the type of legal/medical document using Gemini."""
    prompt = f"""
    Analyze this document and classify it into one of these categories:
    - Legal Contract/Agreement
    - Medical Policy/Insurance
    - Terms of Service
    - Privacy Policy
    - Medical Report/Prescription
    - Government Document
    - Employment Document
    - Other Legal Document
    
    Document text: {text[:1000]}
    
    Respond with just the category name and a brief explanation (1-2 sentences).
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Document Classification (Error: {str(e)})"

def extract_key_entities(text: str, doc_type: str) -> str:
    """Extract domain-specific key entities based on document type."""
    
    entity_prompts = {
        "Legal Contract": """
        Extract these key legal elements from this contract:
        - Parties involved (who are the contracting parties)
        - Contract duration/important dates
        - Payment terms and amounts
        - Key obligations and responsibilities
        - Termination clauses
        - Penalties or consequences for breach
        - Governing law/jurisdiction
        """,
        
        "Medical Policy": """
        Extract these medical policy elements:
        - Coverage details (what's included)
        - Premium amounts and payment schedule
        - Deductibles and co-payments
        - Excluded conditions or treatments
        - Claim filing procedures
        - Network providers and restrictions
        - Policy period and renewal terms
        """,
        
        "Medical Report": """
        Extract these medical elements:
        - Diagnosis or medical findings
        - Prescribed medications and dosages
        - Treatment recommendations
        - Follow-up instructions
        - Test results and their significance
        - Lifestyle recommendations
        - Warning signs to watch for
        """,
        
        "Employment Document": """
        Extract these employment elements:
        - Job title and responsibilities
        - Salary and benefits
        - Work schedule and location
        - Reporting structure
        - Performance expectations
        - Termination conditions
        - Confidentiality requirements
        """
    }
    
    base_prompt = entity_prompts.get(doc_type.split('/')[0], "Extract key information from this document:")
    
    prompt = f"""
    You are an expert legal/medical document analyst. 
    
    {base_prompt}
    
    Document: {text[:4000]}
    
    Present the information in a clear, structured format with bullet points.
    Focus only on information that is explicitly mentioned in the document.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Key entity extraction failed: {str(e)}"

def generate_compliance_checklist(text: str, doc_type: str) -> str:
    """Generate a compliance or action checklist based on document type."""
    
    checklist_prompts = {
        "Legal Contract": """
        Create a practical checklist for someone who needs to comply with this contract:
        - Pre-signing requirements (what to verify before signing)
        - Important deadlines and dates to remember
        - Key obligations they must fulfill
        - Payment schedules and amounts
        - Documentation they need to maintain
        - Warning signs of potential issues
        """,
        
        "Medical Policy": """
        Create an actionable checklist for policy holders:
        - How to file claims (step-by-step process)
        - Important deadlines for claims and renewals
        - What documentation to keep
        - Emergency procedures and contacts
        - Annual requirements (checkups, renewals)
        - Cost-saving tips based on policy terms
        """,
        
        "Medical Report": """
        Create a patient action checklist:
        - Medications to take (names, dosages, timing)
        - Lifestyle changes recommended
        - Follow-up appointments to schedule
        - Symptoms to monitor and report
        - Emergency warning signs requiring immediate attention
        - Questions to ask at next appointment
        """,
        
        "Employment Document": """
        Create an employee checklist:
        - Onboarding requirements to complete
        - Key policies to understand and follow
        - Performance milestones and deadlines
        - Benefits to enroll in
        - Required training or certifications
        - Important contacts and reporting procedures
        """
    }
    
    base_prompt = checklist_prompts.get(doc_type.split('/')[0], "Create an action checklist based on this document:")
    
    prompt = f"""
    {base_prompt}
    
    Document: {text[:4000]}
    
    Format as a clear, actionable checklist with specific items they can act on.
    Use checkboxes (- [ ]) format for each actionable item.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Checklist generation failed: {str(e)}"

def explain_complex_terms(text: str, doc_type: str) -> str:
    """Explain complex legal/medical terms found in the document."""
    
    prompt = f"""
    You are an expert in {doc_type} who specializes in explaining complex terms to everyday people.
    
    Analyze this document and find complex legal, medical, or technical terms that regular people might not understand.
    For each term, provide a simple explanation in plain language.
    
    Document: {text[:4000]}
    
    Format each explanation as:
    **[Term]**: Simple explanation in everyday language
    
    Only include terms that actually appear in the document.
    Focus on the most important or confusing terms (maximum 10 terms).
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Term explanation failed: {str(e)}"

def risk_assessment(text: str, doc_type: str) -> str:
    """Assess potential risks or important considerations."""
    
    risk_prompts = {
        "Legal Contract": """
        Identify potential risks, concerns, or unfavorable terms in this contract:
        - Unusual or strict penalties
        - Vague or ambiguous language that could cause problems
        - Automatic renewal clauses
        - Limitation of liability issues
        - Unfavorable payment terms
        - Difficult termination conditions
        """,
        
        "Medical Policy": """
        Identify potential issues or limitations with this medical policy:
        - Significant coverage gaps or exclusions
        - High out-of-pocket costs or deductibles
        - Restrictive network limitations
        - Complex claim procedures that could lead to denials
        - Pre-authorization requirements
        - Waiting periods for coverage
        """,
        
        "Medical Report": """
        Identify important health considerations and warnings:
        - Serious conditions that require immediate attention
        - Potential drug interactions or side effects
        - Lifestyle changes that are critical for health
        - Symptoms that would require emergency care
        - Follow-up care that shouldn't be delayed
        - Test results that need monitoring
        """,
        
        "Employment Document": """
        Identify potential employment concerns:
        - Unusual restrictive clauses (non-compete, etc.)
        - Unclear job expectations or responsibilities
        - Below-market compensation or benefits
        - Strict performance requirements
        - Limited advancement opportunities
        - Concerning termination conditions
        """
    }
    
    base_prompt = risk_prompts.get(doc_type.split('/')[0], "Identify important considerations and potential risks in this document:")
    
    prompt = f"""
    {base_prompt}
    
    Document: {text[:4000]}
    
    Present as clear warnings or considerations. Be specific about what to watch out for.
    Note: This is informational analysis, not professional legal or medical advice.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Risk assessment failed: {str(e)}"

# ----------------- Enhanced Gemini Helpers -----------------
def ask_gemini(question: str, context: str, language: str = "English", doc_type: str = "") -> str:
    """Ask Gemini a question with enhanced domain-specific context."""
    if not context:
        return "No content extracted from the documents."

    # Enhanced prompt with domain expertise
    domain_context = ""
    if doc_type:
        domain_context = f"You are an expert analyst specializing in {doc_type} documents. "

    prompt = f"""
    {domain_context}You are helping someone understand their document in simple, clear language.
    
    Document Type: {doc_type}
    Document Context: {context[:12000]}
    
    User Question: {question}
    
    Instructions:
    - Provide a detailed, helpful answer in {language}
    - Focus on practical implications and actionable information
    - Explain any complex terms you use
    - If the document doesn't contain the answer, say so clearly
    - Be specific and cite relevant parts of the document when possible
    
    Answer:
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"I apologize, but I encountered an error while analyzing your question: {str(e)}"

def simplify_text(text: str, doc_type: str = "") -> str:
    """Simplify complex legal/medical text into plain language."""
    if not text:
        return "No content to simplify."

    domain_note = f" Focus on {doc_type} terminology and concepts." if doc_type else ""

    prompt = f"""
    Simplify the following text into plain, user-friendly language that anyone can understand.
    {domain_note}
    
    Guidelines:
    - Replace legal/medical jargon with everyday words
    - Break down complex sentences into simpler ones
    - Explain what things mean in practical terms
    - Keep the important information but make it accessible
    
    Text to simplify: {text[:6000]}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Text simplification failed: {str(e)}"

def summarize_text(text: str, doc_type: str = "") -> str:
    """Generate a concise summary of the document(s)."""
    if not text:
        return "No content to summarize."

    domain_focus = ""
    if "Legal Contract" in doc_type:
        domain_focus = "Focus on parties, obligations, terms, and key dates."
    elif "Medical" in doc_type:
        domain_focus = "Focus on coverage, costs, procedures, and important limitations."
    elif "Employment" in doc_type:
        domain_focus = "Focus on role, compensation, responsibilities, and key policies."

    prompt = f"""
    Create a comprehensive summary of this {doc_type} document.
    {domain_focus}
    
    Document: {text[:8000]}
    
    Structure your summary with:
    1. Document Overview (what type of document and main purpose)
    2. Key Points (most important information)
    3. Important Details (dates, amounts, requirements)
    4. Action Items (what the reader needs to do)
    
    Keep it detailed but easy to understand.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Document summary failed: {str(e)}"

# ----------------- Translation -----------------
def translate_text(text: str, target_language: str) -> str:
    """
    Translate text into the selected language.
    Uses Google Cloud Translate if available, else falls back to Gemini.
    """
    if not text or target_language == "English":
        return text

    lang_map = {
        "English": "en",
        "Hindi": "hi",
        "Kannada": "kn",
    }

    # Try Google Cloud Translate first
    if OCR_ENABLED:
        try:
            translate_client = translate.Client()
            target = lang_map.get(target_language, "en")
            result = translate_client.translate(text, target_language=target)
            return result["translatedText"]
        except Exception:
            pass  # Fall back to Gemini

    # Fallback: Gemini-based translation
    prompt = f"""
    Translate the following text into {target_language}.
    Maintain the formatting and structure of the original text.
    Keep technical terms accurate and provide context where needed.
    
    Text to translate: {text[:8000]}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Translation to {target_language} failed: {str(e)}"