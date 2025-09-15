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
    """Extract text from PDFs and images with OCR fallback."""
    all_text = ""
    for file in uploaded_files:
        text = ""
        if file.name.lower().endswith(".pdf"):
            try:
                reader = PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() or ""
            except Exception:
                pass

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

# ----------------- Helpers -----------------
def is_meaningful_content(text: str) -> bool:
    """Check if extracted content is meaningful."""
    if not text or text.strip() == "":
        return False
    text_lower = text.lower().strip()
    empty_patterns = [
        "**", "*", "not specified", "not mentioned", "not found",
        "not available", "no information", "details not provided",
        "information not available", "not listed", "not clearly mentioned"
    ]
    for pattern in empty_patterns:
        if text_lower == pattern or text_lower.startswith(pattern):
            return False
    meaningful_text = text_lower.replace("*", "").replace(" ", "").replace("-", "").replace("•", "")
    return len(meaningful_text) >= 15

# ----------------- Translation -----------------
from langdetect import detect

def translate_text(text, target_language: str):
    """Translate text to target language using Gemini and optionally Google Translate."""
    if not text or target_language == "English":
        return text
    try:
        source_lang = detect(text)
    except:
        source_lang = "en"

    if target_language.lower()[:2] == source_lang.lower()[:2]:
        return text

    lang_map = {"English": "en", "Hindi": "hi", "Kannada": "kn"}
    prompt = f"Translate the following text to {target_language} without changing formatting or meaning:\n\n{text[:4000]}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return text

# ----------------- Document Type Detection -----------------
def detect_document_type(text: str) -> str:
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
    Respond with just the category name.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Document Classification (Error: {str(e)})"

# ----------------- Key Entity Extraction -----------------
def extract_key_entities(text: str, doc_type: str = "", language: str = "English") -> str:
    entity_prompts = {
        "Medical Policy": "Coverage Details, Premium Information, Deductibles, Exclusions, Claim Procedures, Network Providers, Policy Terms, Waiting Periods",
        "Medical Report": "Diagnosis, Medications, Procedures, Follow-up Instructions, Warning Signs, Lifestyle Advice",
        "Legal Contract": "Parties Involved, Contract Duration, Payment Terms, Obligations, Termination Clauses, Penalties, Governing Law"
    }
    base_prompt = entity_prompts.get(doc_type.split('/')[0], "Extract key information:")
    prompt = f"{base_prompt}\nDocument: {text[:4000]}\nFormat as markdown with headings."
    try:
        result = model.generate_content(prompt).text.strip()
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        return f"Key entity extraction failed: {str(e)}"

# ----------------- Compliance Checklist -----------------
def generate_compliance_checklist(text: str, doc_type: str = "", language: str = "English") -> str:
    prompt = f"Create a practical compliance checklist for this {doc_type} document:\n{text[:4000]}\nFormat as numbered list."
    try:
        result = model.generate_content(prompt).text.strip()
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        return f"Checklist generation failed: {str(e)}"

# ----------------- Risk Assessment -----------------
def risk_assessment(text: str, doc_type: str = "", language: str = "English") -> str:
    prompt = f"Identify potential risks, concerns, or limitations in this {doc_type} document:\n{text[:4000]}"
    try:
        result = model.generate_content(prompt).text.strip()
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        return f"Risk assessment failed: {str(e)}"

# ----------------- Explain Complex Terms -----------------
def explain_complex_terms(text: str, doc_type: str = "", language: str = "English") -> str:
    prompt = f"Explain complex terms in this {doc_type} document in simple language:\n{text[:4000]}"
    try:
        result = model.generate_content(prompt).text.strip()
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        return f"Term explanation failed: {str(e)}"

# ----------------- Q&A -----------------
def ask_gemini(question: str, context: str, language: str = "English", doc_type: str = "") -> str:
    if not context:
        return translate_text("No content extracted from the documents.", language)
    domain_context = f"You are an expert in {doc_type} documents. " if doc_type else ""
    prompt = f"{domain_context}Document Type: {doc_type}\nContext: {context[:12000]}\nQuestion: {question}\nAnswer in {language if language != 'English' else 'English'}."
    try:
        result = model.generate_content(prompt).text.strip()
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        return translate_text(f"Q&A failed: {str(e)}", language) if language != "English" else f"Q&A failed: {str(e)}"

# ----------------- Summarize -----------------
def summarize_text(text: str, doc_type: str = "", language: str = "English") -> str:
    if not text:
        return translate_text("No content to summarize.", language)
    prompt = f"Summarize this {doc_type} document with key points and action items:\n{text[:8000]}"
    try:
        result = model.generate_content(prompt).text.strip()
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        return translate_text(f"Document summary failed: {str(e)}", language) if language != "English" else f"Document summary failed: {str(e)}"

# ----------------- Simplify -----------------
def simplify_text(text: str, doc_type: str = "", language: str = "English") -> str:
    if not text:
        return translate_text("No content to simplify.", language)
    prompt = f"Simplify this {doc_type} document into plain language:\n{text[:6000]}"
    try:
        result = model.generate_content(prompt).text.strip()
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        return translate_text(f"Text simplification failed: {str(e)}", language) if language != "English" else f"Text simplification failed: {str(e)}"
