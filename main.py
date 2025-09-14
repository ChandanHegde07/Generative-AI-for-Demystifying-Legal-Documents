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

        # ---------- PDF Handling ----------
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
    if len(meaningful_text) < 15:
        return False
    return True


# ----------------- Structured Entity Extraction -----------------
def extract_key_entities(text: str, doc_type: str) -> dict:
    """Extract structured key entities as dictionary instead of free text."""
    entity_prompts = {
        "Medical Policy": """
        Extract these medical policy elements (return "N/A" if not found):
        Coverage Details, Premium Information, Deductibles and Co-payments,
        Exclusions, Claim Procedures, Network Providers, Policy Terms, Waiting Periods
        """,
        "Medical Report": """
        Extract these discharge summary/medical report elements (return "N/A" if not found):
        Diagnosis, Medications, Procedures, Follow-up Instructions, Warning Signs, Lifestyle Advice
        """,
        "Legal Contract": """
        Extract these contract elements (return "N/A" if not found):
        Parties Involved, Contract Duration, Payment Terms, Obligations,
        Termination Clauses, Penalties, Governing Law
        """
    }

    base_prompt = entity_prompts.get(doc_type.split('/')[0], "Extract key information:")

    prompt = f"""
    {base_prompt}

    Document: {text[:4000]}

    Format as:
    Category: Information (or "N/A" if not found)
    """

    try:
        response = model.generate_content(prompt)
        result = {}
        for line in response.text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key, value = key.strip(), value.strip()
                if is_meaningful_content(value):
                    result[key] = value
        return result
    except Exception as e:
        return {"Error": f"Key entity extraction failed: {str(e)}"}


# ----------------- Document Type Detection -----------------
def detect_document_type(text: str) -> str:
    """Detect the type of document using Gemini."""
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


# ----------------- Checklist -----------------
def generate_compliance_checklist(text: str, doc_type: str) -> list:
    """Generate a compliance or action checklist as list of items."""
    prompt = f"""
    Create a practical checklist based on this {doc_type} document.
    Document: {text[:4000]}
    Format each item as a short bullet point.
    """
    try:
        response = model.generate_content(prompt)
        items = []
        for line in response.text.strip().split("\n"):
            line = line.strip("-• ").strip()
            if len(line) > 5:
                items.append(line)
        return items
    except Exception as e:
        return [f"Checklist generation failed: {str(e)}"]


# ----------------- Risk Assessment -----------------
def risk_assessment(text: str, doc_type: str) -> list:
    """Assess potential risks or considerations as list of items."""
    prompt = f"""
    Identify potential risks, concerns, or limitations in this {doc_type} document.
    Document: {text[:4000]}
    Format each risk as a short bullet point.
    """
    try:
        response = model.generate_content(prompt)
        risks = []
        for line in response.text.strip().split("\n"):
            line = line.strip("-• ").strip()
            if len(line) > 5:
                risks.append(line)
        return risks
    except Exception as e:
        return [f"Risk assessment failed: {str(e)}"]


# ----------------- Terms Explanation -----------------
def explain_complex_terms(text: str, doc_type: str) -> str:
    """Explain complex terms in simple language."""
    prompt = f"""
    Identify complex terms in this {doc_type} document and explain them in plain language.
    Document: {text[:4000]}
    Format as:
    **[Term]**: explanation
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Term explanation failed: {str(e)}"


# ----------------- Q&A -----------------
def ask_gemini(question: str, context: str, language: str = "English", doc_type: str = "") -> str:
    """Ask Gemini a question with domain context."""
    if not context:
        return "No content extracted from the documents."

    domain_context = f"You are an expert in {doc_type} documents. " if doc_type else ""

    prompt = f"""
    {domain_context}
    Document Type: {doc_type}
    Document Context: {context[:12000]}

    User Question: {question}

    Answer in {language}.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Q&A failed: {str(e)}"


# ----------------- Simplify & Summarize -----------------
def summarize_text(text: str, doc_type: str = "") -> str:
    if not text:
        return "No content to summarize."
    prompt = f"Summarize this {doc_type} document: {text[:8000]}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Summary failed: {str(e)}"


# ----------------- Translation -----------------
# ----------------- Enhanced Translation with Retry Logic -----------------
def translate_text(text, target_language: str):
    """
    Enhanced translation with better error handling and retry logic.
    Translate text, dict, or list into the selected language.
    """
    if not text or target_language == "English":
        return text

    # Handle None or empty inputs
    if text is None:
        return None
        
    lang_map = {"English": "en", "Hindi": "hi", "Kannada": "kn"}
    
    # Handle dict
    if isinstance(text, dict):
        translated_dict = {}
        for k, v in text.items():
            try:
                if v and str(v).strip() and not str(v).lower() in ['n/a', 'not found', 'not available']:
                    translated_dict[k] = translate_text(v, target_language)
                else:
                    translated_dict[k] = v  # Keep original for empty/N/A values
            except Exception:
                translated_dict[k] = v  # Keep original on failure
        return translated_dict

    # Handle list
    if isinstance(text, list):
        translated_list = []
        for item in text:
            try:
                if item and str(item).strip():
                    translated_list.append(translate_text(item, target_language))
                else:
                    translated_list.append(item)
            except Exception:
                translated_list.append(item)  # Keep original on failure
        return translated_list

    # Handle string
    text_str = str(text).strip()
    if not text_str or text_str.lower() in ['n/a', 'not found', 'not available', 'not specified']:
        return text
        
    # Try Google Cloud Translation first (if available)
    if OCR_ENABLED:
        for attempt in range(3):
            try:
                translate_client = translate.Client()
                target = lang_map.get(target_language, "en")
                
                # Split long text into chunks to avoid API limits
                if len(text_str) > 5000:
                    chunks = [text_str[i:i+4000] for i in range(0, len(text_str), 4000)]
                    translated_chunks = []
                    for chunk in chunks:
                        if chunk.strip():
                            result = translate_client.translate(chunk, target_language=target)
                            translated_chunks.append(result["translatedText"])
                        else:
                            translated_chunks.append(chunk)
                    return " ".join(translated_chunks)
                else:
                    result = translate_client.translate(text_str, target_language=target)
                    return result["translatedText"]
            except Exception:
                if attempt == 2:
                    break

    # Fallback: Gemini translation with retry logic
    for attempt in range(3):
        try:
            # Enhanced prompt for better translation quality
            prompt = f"""
            Translate the following text from English to {target_language}.
            Rules:
            1. Maintain the original structure, formatting, and meaning
            2. Keep medical/legal terminology accurate
            3. Preserve any formatting like **bold** or bullet points
            4. If there are technical terms that don't have direct translations, provide the closest equivalent
            5. Do not add explanations, just provide the translation
            
            Text to translate:
            {text_str[:8000]}
            
            Translation:
            """
            
            response = model.generate_content(prompt)
            translated = response.text.strip()
            
            # Basic validation - ensure translation isn't empty or error message
            if (translated and 
                len(translated) > 5 and 
                not translated.lower().startswith(("translation failed", "i cannot", "error"))):
                return translated
                
        except Exception:
            if attempt == 2:
                break

    # Final fallback - return original text
    return text