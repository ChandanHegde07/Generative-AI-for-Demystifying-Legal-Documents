import google.generativeai as genai
from PIL import Image
import PyPDF2
import io
from typing import List, Tuple, Optional, Any, Dict 

from src.config import Config 

class DocumentParser:
    def __init__(self):
        self.model = Config.initialize_gemini()
    
    def _extract_text_pdf(self, pdf_file) -> str:
        """Extract text from a PDF file stream using PyPDF2."""
        reader = PyPDF2.PdfReader(pdf_file)
        # Using a more robust way to get text, handling potential None from extract_text()
        extracted_pages = []
        for i, p in enumerate(reader.pages):
            page_text = p.extract_text()
            if page_text:
                extracted_pages.append(f"\n--- Page {i+1} ---\n{page_text}")
            else:
                extracted_pages.append(f"\n--- Page {i+1} ---\n[No readable text on this page]")
        return "\n".join(extracted_pages).strip()


    def _extract_text_image(self, image_file) -> str:
        """Extract text from an image file stream using Gemini Vision."""
        try:
            image_bytes = image_file.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            
            prompt = f"""
            You are an expert OCR system. Extract all text from this image accurately and completely.
            Preserve formatting, line breaks, structure, legal terminology, headers/footers, tables, lists. Note signatures.
            Image filename: {image_file.name}
            Return only the extracted text.
            """
            
            print(f"DEBUG: Calling Gemini Vision for image '{image_file.name}'...")
            response = self.model.generate_content([prompt, image])
            
            extracted_text = response.text.strip()
            print(f"DEBUG: Gemini Vision response for '{image_file.name}':\n{extracted_text[:500]}...")
            
            if not extracted_text:
                print(f"DEBUG: Gemini Vision returned empty text for '{image_file.name}'.")
                return ""
            
            return extracted_text
            
        except Exception as e:
            print(f"ERROR: Gemini Vision failed for '{image_file.name}': {str(e)}")
            return ""

    def extract_text_from_file(self, uploaded_file: Any) -> str:
        """Extract text from a single uploaded file (PDF or Image)."""
        if uploaded_file.type == "application/pdf":
            return self._extract_text_pdf(uploaded_file)
        elif uploaded_file.type.startswith('image/'):
            return self._extract_text_image(uploaded_file)
        elif uploaded_file.type == "text/plain":
            return uploaded_file.getvalue().decode('utf-8')
        raise ValueError(f"Unsupported file type: {uploaded_file.type}")

    def extract_from_multiple_files(self, uploaded_files: List[Any]) -> str:
        """
        Extract and combine text from multiple files. Returns only the combined text content.
        """
        combined_document_content_parts = []
        
        for file in uploaded_files:
            try:
                is_valid, validation_message = Config.validate_file(file)
                if not is_valid:
                    print(f"DEBUG: File validation failed for {file.name}: {validation_message}") 
                    continue
                
                text = self.extract_text_from_file(file)
                if text and text.strip(): 
                    combined_document_content_parts.append(f"\n--- Content from {file.name} ---\n{text}\n")
                else:
                    print(f"DEBUG: No text extracted or text was empty from {file.name}. This file will not contribute to combined text.")
                    
            except Exception as e:
                print(f"DEBUG: Error processing file {file.name} during extraction: {str(e)}")
        
        return "".join(combined_document_content_parts).strip()
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess extracted text."""
        if not text: return ""
        lines = []
        for line in text.split('\n'):
            cleaned_line = ' '.join(line.split()).strip()
            if len(cleaned_line) > 1:
                lines.append(cleaned_line)
        cleaned_text = '\n'.join(lines)
        
        if len(cleaned_text) > Config.MAX_DOCUMENT_LENGTH:
            return cleaned_text[:Config.MAX_DOCUMENT_LENGTH] + "\n\n[Document truncated...]"
        return cleaned_text
    
    def extract_metadata(self, uploaded_file: Any) -> Dict[str, Any]:
        """Extract file metadata."""
        metadata = {
            'filename': uploaded_file.name, 'file_type': uploaded_file.type,
            'file_size_bytes': len(uploaded_file.getvalue()),
            'file_size_mb': round(len(uploaded_file.getvalue()) / (1024 * 1024), 2)
        }
        
        if uploaded_file.type == "application/pdf":
            try:
                # IMPORTANT: Reset file pointer before reading with PyPDF2 if it was read elsewhere
                uploaded_file.seek(0) 
                reader = PyPDF2.PdfReader(uploaded_file)
                metadata['num_pages'] = len(reader.pages)
                if reader.metadata:
                    metadata.update({k.lower().replace('/', 'pdf_'): v for k, v in reader.metadata.items()})
            except Exception as e:
                print(f"DEBUG: Error extracting PDF metadata: {e}")
                metadata['num_pages'] = 'Unknown'
        
        elif uploaded_file.type.startswith('image/'):
            try:
                # IMPORTANT: Reset file pointer before reading with PIL if it was read elsewhere
                uploaded_file.seek(0)
                img = Image.open(io.BytesIO(uploaded_file.getvalue()))
                metadata.update({'image_dimensions': f"{img.width}x{img.height}", 'image_mode': img.mode, 'image_format': img.format})
            except Exception as e:
                print(f"DEBUG: Error extracting image metadata: {e}")
                metadata['image_dimensions'] = 'Unknown'
        
        return metadata
    
    def validate_extracted_text(self, text: str) -> Tuple[bool, str]:
        """Validate that extracted text is meaningful."""
        cleaned_text = text.strip() 
        
        print(f"DEBUG VALIDATION: Cleaned text length: {len(cleaned_text)}")
        print(f"DEBUG VALIDATION: Cleaned text start (500 chars): {cleaned_text[:500].replace('\n', ' ')}") 
        
        if not cleaned_text:
            print("DEBUG VALIDATION: Failed: No text or empty after strip.")
            return False, "No text was extracted from the document."
        
        # Validate against configurable minimum character length
        if len(cleaned_text) < Config.MIN_TEXT_FOR_ANALYSIS: 
            print(f"DEBUG VALIDATION: Failed: Text too short, {len(cleaned_text)} characters. Minimum is {Config.MIN_TEXT_FOR_ANALYSIS}.")
            return False, f"Extracted text is too short to be meaningful ({len(cleaned_text)} characters found, minimum is {Config.MIN_TEXT_FOR_ANALYSIS})."
        
        # REMOVED THE LEGAL/HEALTHCARE INDICATOR CHECK AS IT WAS OVERLY STRICT FOR THIS USE CASE
        # AND THE AI CLASSIFIER IS BETTER SUITED FOR SEMANTIC DOCUMENT TYPE RECOGNITION.
        # The error "Text may not be a legal/healthcare document or OCR quality poor" was specifically
        # coming from this removed block, incorrectly failing valid structured documents.
        
        print("DEBUG VALIDATION: Passed.")
        return True, "Text extraction appears successful."