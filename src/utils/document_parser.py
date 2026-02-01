import google.generativeai as genai
from PIL import Image
import io
from typing import List, Tuple, Any, Dict
import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
import fitz  
import os 

from src.config import Config

class DocumentParser:
    def __init__(self):
        self.model = Config.initialize_gemini()
        self.vision_client = None
        self.enable_pii_anonymization = Config.ENABLE_PII_ANONYMIZATION
        self.pii_mapping = {}
        
        if self.enable_pii_anonymization:
            from src.utils.pii_anonymizer import PIIAnonymizer
            self.anonymizer = PIIAnonymizer()
        
        if Config.USE_GOOGLE_VISION_OCR:
            try:
                if "gcp_service_account" in st.secrets:
                    creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
                    self.vision_client = vision.ImageAnnotatorClient(credentials=creds)
                    print("Successfully initialized Google Cloud Vision client.")
                else:
                    print("WARNING: `USE_GOOGLE_VISION_OCR` is True, but `gcp_service_account` is not found in secrets. OCR will fall back to Gemini Vision.")
            except Exception as e:
                print(f"ERROR: Failed to initialize Google Cloud Vision client: {e}. OCR will fall back to Gemini Vision.")

    def _extract_text_pdf(self, pdf_file) -> str:
        print("DEBUG: Attempting PDF text extraction with PyMuPDF...")
        try:
            pdf_file.seek(0)
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            full_text = [page.get_text() for page in doc]
            combined_text = "\n".join(full_text)
            is_scanned = all(len(page_text.strip()) < 10 for page_text in full_text)
            print(f"DEBUG: PyMuPDF extracted {len(combined_text)} characters.")
            if is_scanned:
                print("DEBUG: PyMuPDF found no significant text; treating as scanned and falling back to OCR.")
                pdf_file.seek(0)
                return self._ocr_scanned_pdf(pdf_file)
            return "\n".join(f"\n--- Page {i+1} ---\n{text}" for i, text in enumerate(full_text)).strip()
        except Exception as e:
            print(f"ERROR: PyMuPDF failed to process the PDF directly: {e}. Attempting full OCR as a fallback.")
            pdf_file.seek(0)
            return self._ocr_scanned_pdf(pdf_file)

    def _ocr_scanned_pdf(self, pdf_file) -> str:
        if Config.USE_GOOGLE_VISION_OCR and self.vision_client:
            try:
                print("DEBUG: Using Google Cloud Vision for scanned PDF...")
                pdf_file.seek(0)
                pdf_bytes = pdf_file.read()
                input_config = vision.InputConfig(content=pdf_bytes, mime_type='application/pdf')
                feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
                response = self.vision_client.batch_annotate_files(requests=[{'input_config': input_config, 'features': [feature]}])
                full_text = "".join(page_response.full_text_annotation.text for r in response.responses for page_response in r.responses)
                if full_text: return full_text
            except Exception as e:
                print(f"WARNING: Google Cloud Vision PDF processing failed: {e}. Falling back to Gemini.")
        print("DEBUG: Using Gemini for scanned PDF...")
        try:
            pdf_file.seek(0)
            pdf_part = {"mime_type": "application/pdf", "data": pdf_file.getvalue()}
            prompt = "Extract all text from this PDF document. Provide only the text content, maintaining the original structure as much as possible."
            response = self.model.generate_content([prompt, pdf_part])
            return response.text
        except Exception as e:
            print(f"ERROR: Gemini PDF extraction failed: {e}")
            return "[Failed to extract text from scanned PDF]"

    def _extract_text_image(self, image_file) -> str:
        if Config.USE_GOOGLE_VISION_OCR and self.vision_client:
            return self._extract_text_image_google_vision(image_file)
        else:
            print("DEBUG: Using Gemini Vision for image OCR...")
            return self._extract_text_image_gemini_vision(image_file)

    def _extract_text_image_google_vision(self, image_file) -> str:
        try:
            print("DEBUG: Using Google Cloud Vision for image...")
            image_file.seek(0)
            image_bytes = image_file.read()
            image = vision.Image(content=image_bytes)
            response = self.vision_client.document_text_detection(image=image)
            if response.error.message:
                raise Exception(f"Vision API Error: {response.error.message}")
            return response.full_text_annotation.text
        except Exception as e:
            print(f"WARNING: Google Cloud Vision failed for image: {e}. Falling back to Gemini.")
            return self._extract_text_image_gemini_vision(image_file)

    def _extract_text_image_gemini_vision(self, image_file) -> str:
        try:
            image_file.seek(0)
            image = Image.open(image_file)
            prompt = """
            You are a professional OCR system. Extract ALL text from this image with perfect accuracy.
            CRITICAL REQUIREMENTS:
            1. Return ONLY the extracted text - no explanations or comments.
            2. Preserve exact formatting, line breaks, and spacing.
            3. Maintain document structure (headers, body text, lists, tables).
            """
            response = self.model.generate_content([prompt, image])
            return response.text.strip()
        except Exception as e:
            print(f"ERROR: Gemini Vision OCR failed: {str(e)}")
            return f"[Failed to extract text from image: {image_file.name}]"

    def extract_text_from_file(self, uploaded_file: Any) -> str:
        """
        Extracts text from a file object. This method is now smart enough to handle
        both Streamlit UploadedFile objects and standard Python file objects.
        """
        file_type = ""
        filename = ""
        
        if hasattr(uploaded_file, 'type'):
            file_type = uploaded_file.type
            filename = uploaded_file.name
        elif hasattr(uploaded_file, 'name'):
            filename = uploaded_file.name
            extension = os.path.splitext(filename)[1].lower()
            mime_map = {
                '.pdf': 'application/pdf',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.txt': 'text/plain',
            }
            file_type = mime_map.get(extension, 'unknown')
        else:
            raise ValueError("Unsupported file object type provided to DocumentParser.")
            
        print(f"DEBUG: Processing file '{filename}' with inferred type '{file_type}'")

        if file_type == "application/pdf":
            text = self._extract_text_pdf(uploaded_file)
        elif file_type.startswith('image/'):
            text = self._extract_text_image(uploaded_file)
        elif file_type == "text/plain":
            if hasattr(uploaded_file, 'getvalue'):
                text = uploaded_file.getvalue().decode('utf-8')
            else:
                uploaded_file.seek(0)
                text = uploaded_file.read().decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_type} for file: {filename}")
        
        # Apply PII anonymization if enabled
        if hasattr(self, 'enable_pii_anonymization') and hasattr(self, 'anonymizer') and self.enable_pii_anonymization and self.anonymizer and text:
            anonymized_text, pii_mapping = self.anonymizer.anonymize(text)
            if hasattr(self, 'pii_mapping'):
                self.pii_mapping.update(pii_mapping)
            else:
                self.pii_mapping = pii_mapping
            return anonymized_text
        
        return text
    
    def get_pii_mapping(self) -> Dict[str, str]:
        """Get the PII mapping for extracted documents"""
        if hasattr(self, 'pii_mapping'):
            return self.pii_mapping
        return {}
    
    def get_pii_summary(self) -> str:
        """Get a formatted summary of detected PII"""
        if hasattr(self, 'anonymizer'):
            return self.anonymizer.get_pii_summary()
        return "PII anonymization is disabled."
    
    def deanonymize_text(self, text: str) -> str:
        """Restore original PII in text"""
        if hasattr(self, 'anonymizer') and hasattr(self, 'pii_mapping') and self.anonymizer and self.pii_mapping:
            return self.anonymizer.deanonymize(text, self.pii_mapping)
        return text

    def extract_from_multiple_files(self, uploaded_files: List[Any]) -> str:
        """Extract text from multiple uploaded files and combine them"""
        combined_text = []
        
        for file in uploaded_files:
            file_text = self.extract_text_from_file(file)
            if file_text:
                combined_text.append(file_text)
        
        return "\n\n---\n\n".join(combined_text)
    
    def preprocess_text(self, text: str) -> str:
        if not text: return ""
        cleaned_text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
        if len(cleaned_text) > Config.MAX_DOCUMENT_LENGTH:
            cleaned_text = cleaned_text[:Config.MAX_DOCUMENT_LENGTH] + "\n\n[Document truncated...]"
        return cleaned_text
    
    def validate_extracted_text(self, text: str) -> Tuple[bool, str]:
        if not text or len(text.strip()) < Config.MIN_TEXT_FOR_ANALYSIS:
            return False, f"Text is too short for analysis (minimum {Config.MIN_TEXT_FOR_ANALYSIS} characters required)."
        return True, "Text is valid for analysis."