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
        return "\n".join([f"\n--- Page {i+1} ---\n{p.extract_text() or ''}" for i, p in enumerate(reader.pages)]).strip()

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
            print(f"DEBUG: Gemini Vision response for '{image_file.name}':\n{extracted_text[:500]}...") # Print first 500 chars
            
            if not extracted_text:
                print(f"DEBUG: Gemini Vision returned empty text for '{image_file.name}'.")
                return ""
            
            return extracted_text
            
        except Exception as e:
            # Catch specific errors from Gemini API for better debugging
            print(f"ERROR: Gemini Vision failed for '{image_file.name}': {str(e)}")
            return "" # Return empty string on failure

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
        Internal logging for failed files can be added if needed, but not part of the return value.
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
        lines = [' '.join(line.split()) for line in text.split('\n') if len(' '.join(line.split())) > 2]
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
                reader = PyPDF2.PdfReader(uploaded_file)
                metadata['num_pages'] = len(reader.pages)
                if reader.metadata:
                    metadata.update({k.lower().replace('/', 'pdf_'): v for k, v in reader.metadata.items()})
            except Exception:
                metadata['num_pages'] = 'Unknown'
        
        elif uploaded_file.type.startswith('image/'):
            try:
                img = Image.open(io.BytesIO(uploaded_file.getvalue()))
                metadata.update({'image_dimensions': f"{img.width}x{img.height}", 'image_mode': img.mode, 'image_format': img.format})
            except Exception:
                metadata['image_dimensions'] = 'Unknown'
        
        return metadata
    
    def validate_extracted_text(self, text: str) -> Tuple[bool, str]:
        """Validate that extracted text is meaningful."""
        print(f"DEBUG VALIDATION: Text length: {len(text)}")
        print(f"DEBUG VALIDATION: Text start (100 chars): {text[:100].replace('\n', ' ')}") 
        
        if not text or not text.strip():
            print("DEBUG VALIDATION: Failed: No text or empty after strip.")
            return False, "No text was extracted from the document."
        
        words = text.split()
        if len(words) < 10: 
            print(f"DEBUG VALIDATION: Failed: Text too short, {len(words)} words.")
            return False, "Extracted text is too short to be meaningful."
        
        legal_healthcare_indicators = [
            'agreement', 'contract', 'party', 'clause', 'section', 'terms', 'conditions', 'legal', 'law', 'court', 
            'rights', 'obligations', 'liability', 'breach', 'notice', 'date', 
            'policy', 'patient', 'medical', 'diagnosis', 'treatment', 'insurance', 
            'claim', 'provider', 'beneficiary', 'hospital', 'doctor', 'prescription',
            'health', 'coverage', 'service', 'deductible', 'copay', 'report', 'consent', 'record' # Added more
        ]
        
        text_lower = text.lower()
        
        found_indicators = sum(1 for ind in legal_healthcare_indicators if ind in text_lower)
        print(f"DEBUG VALIDATION: Found legal/healthcare indicators count: {found_indicators}")
        print(f"DEBUG VALIDATION: Indicators found: {[ind for ind in legal_healthcare_indicators if ind in text_lower]}")
        
        # Relaxed threshold to 1 for maximum leniency
        if found_indicators < 1: 
            print("DEBUG VALIDATION: Failed: Less than 1 legal/healthcare indicator found.")
            return False, "Text may not be a legal/healthcare document or OCR quality poor."
        
        print("DEBUG VALIDATION: Passed.")
        return True, "Text extraction appears successful."