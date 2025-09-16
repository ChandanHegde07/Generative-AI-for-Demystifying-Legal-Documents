from langdetect import detect
from src.config import GEMINI_MODEL, LANG_MAP

def translate_text(text, target_language: str):
    """Translate text to target language using Gemini."""
    if not text or target_language == "English":
        return text
    
    try:
        source_lang = detect(text)
    except:
        source_lang = "en" # Default to English if detection fails

    # Check if target language is already the source language (case-insensitive for first two chars)
    # The original logic used .lower()[:2] for this check.
    if LANG_MAP.get(target_language, "en").lower()[:2] == source_lang.lower()[:2]:
        return text

    # The original implementation solely used the Gemini model for translation
    prompt = f"Translate the following text to {target_language} without changing formatting or meaning:\n\n{text[:4000]}"
    try:
        response = GEMINI_MODEL.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini translation failed: {e}")
        return text # Return original text on failure