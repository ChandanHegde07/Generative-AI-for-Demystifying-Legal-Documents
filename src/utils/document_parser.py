from pypdf import PdfReader
# Removed imports for OCR_ENABLED, VISION_CLIENT as they are no longer used here for actual OCR.
# However, to avoid import errors if config still defined them, we keep the original import structure but rely on False/None from config.
from src.config import OCR_ENABLED, VISION_CLIENT # Keeping for structural consistency, but behavior relies on config.py now setting them to False/None

def extract_text_from_files(uploaded_files) -> str:
    """Extract text from PDFs using pypdf. Image files will not be processed for text."""
    all_text = ""
    for file in uploaded_files:
        text = ""
        file_extension = file.name.lower()

        if file_extension.endswith(".pdf"):
            try:
                reader = PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() or ""
                if not text.strip():
                    text = f"[No selectable text found in PDF: {file.name}. OCR functionality is disabled.]"
                    print(text)
            except Exception as e:
                text = f"[Error reading PDF {file.name}: {e}. OCR functionality is disabled.]"
                print(text)

        elif file_extension.endswith((".jpg", ".jpeg", ".png")):
            text = f"[Text extraction from image files ({file.name}) is disabled as Google Cloud Vision OCR is not configured.]"
            print(text)
        
        if text.strip() and not text.startswith("["): # Only add meaningful extracted text
            all_text += text.strip() + "\n\n--- End of Document ---\n\n"
        elif text.startswith("["): # Add status messages for user feedback
             all_text += text.strip() + "\n\n--- End of Document ---\n\n"
        else:
            all_text += f"[Could not extract any meaningful text from {file.name}]\n\n--- End of Document ---\n\n"


    return all_text.strip()