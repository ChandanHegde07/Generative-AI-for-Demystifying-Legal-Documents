import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Tuple, Any, Dict

load_dotenv()

class Config:
    _GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not _GEMINI_API_KEY:
        raise ValueError("Google API key not found. Please set it in your .env file as GOOGLE_API_KEY.")
    
    GEMINI_MODEL_NAME: str = "gemini-1.5-pro"
    
    # Model parameters for Gemini (can be made class attributes for easier modification)
    GEMINI_TEMPERATURE: float = 0.1      # Low temperature for consistent legal analysis
    GEMINI_MAX_OUTPUT_TOKENS: int = 8192
    GEMINI_TOP_K: int = 40
    GEMINI_TOP_P: float = 0.95

    @staticmethod
    def initialize_gemini():
        genai.configure(api_key=Config._GEMINI_API_KEY)
        return genai.GenerativeModel(Config.GEMINI_MODEL_NAME)

    OCR_ENABLED: bool = False
    VISION_CLIENT = None      # Placeholder for a Vision client
    TRANSLATE_CLIENT = None   # Placeholder for a Translate client

    LANG_MAP: Dict[str, str] = {"English": "en", "Hindi": "hi", "Kannada": "kn"}
    SUPPORTED_LANGUAGES: List[str] = list(LANG_MAP.keys()) 

    MAX_DOCUMENT_LENGTH: int = 300000 

    SUPPORTED_DOCUMENT_TYPES: List[str] = [
        "Contract Agreement", "Legal Notice", "Terms of Service", "Privacy Policy",
        "Employment Agreement", "Lease Agreement", "Insurance Policy", "Healthcare Document",
        "Government Legal Document", "Court Document", "Corporate Legal Document",
        "Other Legal Document"
    ]

    @staticmethod
    def get_model_settings() -> Dict[str, Any]:
        """Get all relevant model configuration settings."""
        return {
            "model_name": Config.GEMINI_MODEL_NAME,
            "api_key_set": bool(Config._GEMINI_API_KEY),
            "temperature": Config.GEMINI_TEMPERATURE,
            "max_output_tokens": Config.GEMINI_MAX_OUTPUT_TOKENS,
            "top_k": Config.GEMINI_TOP_K,
            "top_p": Config.GEMINI_TOP_P
        }

    @staticmethod
    def validate_file(uploaded_file: Any) -> Tuple[bool, str]:
        if not uploaded_file:
            return False, "No file provided."
        
        MAX_FILE_SIZE_MB = 25
        if len(uploaded_file.getvalue()) > MAX_FILE_SIZE_MB * 1024 * 1024:
            return False, f"File size exceeds {MAX_FILE_SIZE_MB}MB limit."
        
        supported_mime_types = ["application/pdf", "image/jpeg", "image/png", "image/gif", "text/plain"]
        if uploaded_file.type not in supported_mime_types:
            return False, f"Unsupported file type: {uploaded_file.type}. Supported types are: {', '.join(supported_mime_types)}"
        
        return True, "File is valid."