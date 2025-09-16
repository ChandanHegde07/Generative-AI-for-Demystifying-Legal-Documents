# This main.py acts as a facade, importing and re-exporting functions
# from the 'src' directory to maintain compatibility with app.py.

# Document Extraction
from src.utils.document_parser import extract_text_from_files

# Helpers (though not directly used in app.py's main logic, it's good practice to list if part of the original)
# from src.utils.helpers import is_meaningful_content

# Translation (imported by app.py, though its logic isn't explicitly called there directly)
from src.utils.translator import translate_text

# AI Processor Services
from src.services.ai_processor import (
    detect_document_type,
    extract_key_entities,
    generate_compliance_checklist,
    explain_complex_terms,
    risk_assessment,
    summarize_text,
    simplify_text,
)

# Chat Service
from src.services.chat_service import ask_gemini

# Note: extract_text_from_pdfs is an alias in app.py for extract_text_from_files
# from main import extract_text_from_files as extract_text_from_pdfs
# This means app.py still works by importing 'extract_text_from_files' from this 'main.py' file.