from src.config import GEMINI_MODEL
from src.utils.translator import translate_text

def ask_gemini(question: str, context: str, language: str = "English", doc_type: str = "") -> str:
    if not context:
        # Original code used conditional translate, preserving that
        return translate_text("No content extracted from the documents.", language)
    domain_context = f"You are an expert in {doc_type} documents. " if doc_type else ""
    prompt = f"{domain_context}Document Type: {doc_type}\nContext: {context[:12000]}\nQuestion: {question}\nAnswer in {language if language != 'English' else 'English'}."
    try:
        result = GEMINI_MODEL.generate_content(prompt).text.strip()
        # Original code used conditional translate, preserving that
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        # Original code used conditional translate, preserving that
        return translate_text(f"Q&A failed: {str(e)}", language) if language != "English" else f"Q&A failed: {str(e)}"