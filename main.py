# main.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
from pypdf import PdfReader

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("Google API key not found. Please set it in your .env file as GOOGLE_API_KEY.")

# Configure Gemini
genai.configure(api_key=API_KEY)

# Load model
model = genai.GenerativeModel("gemini-1.5-flash")


def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()


def ask_gemini(question: str, context: str, language: str = "English") -> str:
    """
    Ask Gemini a question with PDF context and return the answer in the selected language.
    :param question: User query
    :param context: Extracted PDF text
    :param language: Target language for the answer
    """
    if not context:
        return "No content extracted from the document."

    prompt = f"""
    You are an AI assistant specialized in legal document analysis.
    Context: {context[:8000]}  # Limit context size for efficiency
    Question: {question}
    Answer clearly and concisely in {language}.
    """

    response = model.generate_content(prompt)
    return response.text.strip()