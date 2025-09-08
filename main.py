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
def extract_text_from_pdfs(pdf_files) -> str:
    """
    Extract text from multiple PDF files.
    Falls back to OCR if needed and OCR is enabled.
    Returns merged text from all files.
    """
    all_text = ""

    for pdf_file in pdf_files:
        text = ""

        # Try normal PDF text extraction
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() or ""
        except Exception:
            pass

        # Fallback to OCR if no text
        if OCR_ENABLED and not text.strip():
            try:
                pdf_file.seek(0)
                client = vision.ImageAnnotatorClient()
                content = pdf_file.read()
                image = vision.Image(content=content)
                response = client.text_detection(image=image)
                text = response.full_text_annotation.text if response.text_annotations else ""
            except Exception as e:
                text = f"[OCR failed: {e}]"

        all_text += text.strip() + "\n\n--- End of Document ---\n\n"

    return all_text.strip()

# ----------------- Gemini Helpers -----------------
def ask_gemini(question: str, context: str, language: str = "English") -> str:
    """Ask Gemini a question with merged PDF context."""
    if not context:
        return "No content extracted from the documents."

    prompt = f"""
    You are an AI assistant specialized in legal and medical document analysis.
    Context: {context[:15000]}  
    Question: {question}
    Answer clearly and concisely in {language}.
    """

    response = model.generate_content(prompt)
    return response.text.strip()

def simplify_text(text: str) -> str:
    """Simplify complex legal/medical text into plain language."""
    if not text:
        return "No content to simplify."

    prompt = f"Simplify the following text into plain, user-friendly language:\n\n{text[:5000]}"
    response = model.generate_content(prompt)
    return response.text.strip()

def summarize_text(text: str) -> str:
    """Generate a concise summary of the document(s)."""
    if not text:
        return "No content to summarize."

    prompt = f"Summarize the following document(s) into key points:\n\n{text[:5000]}"
    response = model.generate_content(prompt)
    return response.text.strip()

# ----------------- Translation -----------------
def translate_text(text: str, target_language: str) -> str:
    """
    Translate text into the selected language.
    Uses Google Cloud Translate if available, else falls back to Gemini.
    """
    if not text:
        return "No content to translate."

    lang_map = {
        "English": "en",
        "Hindi": "hi",
        "Kannada": "kn",
    }

    if OCR_ENABLED:
        try:
            translate_client = translate.Client()
            target = lang_map.get(target_language, "en")
            result = translate_client.translate(text, target_language=target)
            return result["translatedText"]
        except Exception as e:
            return f"[Translation failed: {e}]"

    # Fallback: Gemini-based translation
    prompt = f"Translate the following text into {target_language}:\n\n{text[:5000]}"
    response = model.generate_content(prompt)
    return response.text.strip()