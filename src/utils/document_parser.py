import google.generativeai as genai
from PIL import Image
import io
from typing import List, Tuple, Any, Dict
import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
import fitz

from src.config import Config

class DocumentParser:
    def __init__(self):
        self.model = Config.initialize_gemini()
        self.vision_client = None
        if Config.USE_GOOGLE_VISION_OCR:
            try:
                if "gcp_service_account" in st.secrets:
                    creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
                    self.vision_client = vision.ImageAnnotatorClient(credentials=creds)
                    print("✅ Successfully initialized Google Cloud Vision client.")
                else:
                    print("⚠️ WARNING: `USE_GOOGLE_VISION_OCR` is True, but `gcp_service_account` is not found in secrets. OCR will fall back to Gemini Vision.")
            except Exception as e:
                print(f"❌ ERROR: Failed to initialize Google Cloud Vision client: {e}. OCR will fall back to Gemini Vision.")

    def _extract_text_pdf(self, pdf_file) -> str:
        try:
            pdf_file.seek(0)
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            
            full_text = []
            is_scanned = True
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text.strip():
                    is_scanned = False
                full_text.append(page_text)
            
            if is_scanned:
                print("DEBUG: PDF appears to be image-based. Applying full OCR...")
                pdf_file.seek(0)
                return self._ocr_scanned_pdf(pdf_file)

            return "\n".join(f"\n--- Page {i+1} ---\n{text}" for i, text in enumerate(full_text)).strip()
        except Exception as e:
            print(f"ERROR: Failed to process PDF with PyMuPDF: {e}. Attempting OCR as a fallback.")
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
                if full_text:
                    print(f"DEBUG: Cloud Vision extracted {len(full_text)} characters from PDF.")
                    return full_text
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
        if uploaded_file.type == "application/pdf":
            return self._extract_text_pdf(uploaded_file)
        elif uploaded_file.type.startswith('image/'):
            return self._extract_text_image(uploaded_file)
        elif uploaded_file.type == "text/plain":
            return uploaded_file.getvalue().decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {uploaded_file.type}")

    def preprocess_text(self, text: str) -> str:
        if not text:
            return ""
        cleaned_text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
        if len(cleaned_text) > Config.MAX_DOCUMENT_LENGTH:
            cleaned_text = cleaned_text[:Config.MAX_DOCUMENT_LENGTH] + "\n\n[Document truncated...]"
        return cleaned_text
    
    def validate_extracted_text(self, text: str) -> Tuple[bool, str]:
        if not text or len(text.strip()) < Config.MIN_TEXT_FOR_ANALYSIS:
            return False, f"Text is too short for analysis (minimum {Config.MIN_TEXT_FOR_ANALYSIS} characters required)."
        return True, "Text is valid for analysis."