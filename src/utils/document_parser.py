from pypdf import PdfReader
from src.config import OCR_ENABLED, VISION_CLIENT

def extract_text_from_files(uploaded_files) -> str:
    """Extract text from PDFs and images with OCR fallback."""
    all_text = ""
    for file in uploaded_files:
        text = ""
        file_extension = file.name.lower()

        if file_extension.endswith(".pdf"):
            try:
                reader = PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() or ""
            except Exception as e:
                print(f"Error reading PDF with pypdf: {e}")
                pass # Try OCR if pypdf fails or extracts no text

            if OCR_ENABLED and not text.strip() and VISION_CLIENT:
                print(f"No text extracted by pypdf for {file.name}, attempting OCR...")
                try:
                    file.seek(0) # Reset file pointer for OCR
                    content = file.read()
                    image = VISION_CLIENT.document_text_detection(image=VISION_CLIENT.image(content=content))
                    text = image.full_text_annotation.text if image.text_annotations else ""
                    if text.strip():
                        print(f"OCR successfully extracted text from {file.name}.")
                    else:
                        print(f"OCR also failed to extract meaningful text from {file.name}.")
                except Exception as e:
                    text = f"[OCR for PDF failed: {e}]"
                    print(text)
            elif OCR_ENABLED and not VISION_CLIENT:
                print("OCR is enabled, but Google Cloud Vision client is not initialized.")


        elif file_extension.endswith((".jpg", ".jpeg", ".png")):
            if OCR_ENABLED and VISION_CLIENT:
                try:
                    file.seek(0) # Reset file pointer for OCR
                    content = file.read()
                    image = VISION_CLIENT.document_text_detection(image=VISION_CLIENT.image(content=content))
                    text = image.full_text_annotation.text if image.text_annotations else ""
                    if text.strip():
                        print(f"OCR successfully extracted text from {file.name}.")
                    else:
                        print(f"OCR failed to extract meaningful text from {file.name}.")
                except Exception as e:
                    text = f"[Image OCR failed: {e}]"
                    print(text)
            elif OCR_ENABLED and not VISION_CLIENT:
                text = "[Image files require Google Cloud Vision for text extraction, but client is not initialized.]"
                print(text)
            else:
                text = "[Image files require Google Cloud Vision for text extraction. OCR is disabled.]"
                print(text)
        
        # Only add meaningful text to all_text
        if text.strip():
            all_text += text.strip() + "\n\n--- End of Document ---\n\n"
        else:
            all_text += f"[Could not extract any meaningful text from {file.name}]\n\n--- End of Document ---\n\n"

    return all_text.strip()