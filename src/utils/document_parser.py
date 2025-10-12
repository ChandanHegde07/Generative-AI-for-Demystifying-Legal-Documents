import google.generativeai as genai
from PIL import Image
import PyPDF2
import io
import requests
import json
import re
from typing import List, Tuple, Optional, Any, Dict 

from src.config import Config 
from src.utils.pii_anonymizer import PIIAnonymizer

class DocumentParser:
    def __init__(self, ocr_method='cloud_vision', enable_pii_anonymization=None):
        """
        Initialize with OCR options:
        - 'cloud_vision': Google Cloud Vision API (primary, with Pillow fallback)
        - 'gemini_simple': Gemini API with OCR-optimized prompts
        - 'vision_rest': Direct REST API calls to Vision API
        - 'gemini_original': Original implementation
        
        Args:
            ocr_method: OCR method to use
            enable_pii_anonymization: Enable PII detection (for tracking only, not for extraction)
        """
        self.ocr_method = ocr_method
        
        # PII Anonymization - Only for tracking, NOT for text extraction
        # (Anonymization happens at AI service level before Gemini calls)
        self.enable_pii_anonymization = False  # Disabled at extraction level
        self.anonymizer = PIIAnonymizer()  # Keep for tracking purposes
        self.pii_mapping: Dict[str, str] = {}
        
        # Initialize Vision client if using cloud_vision
        if ocr_method == 'cloud_vision':
            self.vision_client = Config.initialize_vision()
        else:
            self.vision_client = None
        
        # Initialize Gemini for gemini methods
        if ocr_method in ['gemini_simple', 'gemini_original']:
            genai.configure(api_key=Config._GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def _extract_text_pdf(self, pdf_file) -> str:
        """Extract text from PDF using PyPDF2, with OCR fallback for scanned PDFs"""
        reader = PyPDF2.PdfReader(pdf_file)
        extracted_pages = []
        has_no_text = True  # Track if PDF has any extractable text
        
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            
            # If page has text, use it
            if page_text and len(page_text.strip()) > 20:
                extracted_pages.append(f"\n--- Page {i+1} ---\n{page_text}")
                has_no_text = False
            else:
                extracted_pages.append(None)  # Mark for OCR later
        
        # If entire PDF has no extractable text, it's a scanned PDF - use OCR
        if has_no_text:
            print("DEBUG: PDF appears to be scanned/image-based. Using OCR on entire PDF...")
            ocr_text = self._extract_text_from_scanned_pdf(pdf_file)
            if ocr_text and len(ocr_text.strip()) > 10:
                return ocr_text
            else:
                return "[No readable text could be extracted from this PDF]"
        
        # Otherwise, use OCR only on pages without text
        final_pages = []
        for i, page_content in enumerate(extracted_pages):
            if page_content is not None:
                final_pages.append(page_content)
            else:
                # Try OCR on this specific page
                print(f"DEBUG: Page {i+1} has no text. Attempting OCR...")
                ocr_page_text = self._extract_text_from_pdf_page_ocr(pdf_file, i)
                if ocr_page_text and len(ocr_page_text.strip()) > 10:
                    final_pages.append(f"\n--- Page {i+1} (OCR) ---\n{ocr_page_text}")
                else:
                    final_pages.append(f"\n--- Page {i+1} ---\n[No readable text on this page]")
        
        return "\n".join(final_pages).strip()
    
    def _extract_text_from_scanned_pdf(self, pdf_file) -> str:
        """Extract text from scanned PDF using Cloud Vision or Gemini OCR"""
        try:
            # Method 1: Try Cloud Vision API (best for scanned PDFs)
            if self.vision_client:
                print("DEBUG: Using Cloud Vision API for scanned PDF...")
                
                from google.cloud import vision
                
                pdf_file.seek(0)
                pdf_bytes = pdf_file.read()
                
                # Cloud Vision supports direct PDF processing
                input_config = vision.InputConfig(
                    content=pdf_bytes,
                    mime_type='application/pdf'
                )
                
                feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
                request = vision.AnnotateFileRequest(
                    input_config=input_config,
                    features=[feature]
                )
                
                response = self.vision_client.batch_annotate_files(requests=[request])
                
                extracted_text = []
                for page_response in response.responses[0].responses:
                    if page_response.full_text_annotation:
                        extracted_text.append(page_response.full_text_annotation.text)
                
                if extracted_text:
                    full_text = "\n\n".join(extracted_text)
                    print(f"DEBUG: Cloud Vision extracted {len(full_text)} characters from PDF")
                    return full_text
            
            # Method 2: Fallback to Gemini with PDF
            print("DEBUG: Using Gemini fallback for scanned PDF...")
            return self._extract_text_from_pdf_with_gemini(pdf_file)
            
        except Exception as e:
            print(f"WARNING: Cloud Vision PDF processing failed: {str(e)}")
            print("DEBUG: Falling back to Gemini...")
            return self._extract_text_from_pdf_with_gemini(pdf_file)
    
    def _extract_text_from_pdf_page_ocr(self, pdf_file, page_num: int) -> str:
        """OCR a specific PDF page (fallback for mixed text/image PDFs)"""
        # For now, return empty - full PDF OCR is more reliable
        # This can be enhanced later if needed
        return ""
    
    def _extract_text_from_pdf_with_gemini(self, pdf_file) -> str:
        """Use Gemini to extract text from PDF (fallback method)"""
        try:
            pdf_file.seek(0)
            pdf_bytes = pdf_file.read()
            
            # Upload PDF to Gemini
            import google.generativeai as genai
            
            # Create a temporary file-like object for Gemini
            pdf_part = {
                "mime_type": "application/pdf",
                "data": pdf_bytes
            }
            
            prompt = """Extract all text from this PDF document. 
            
Provide the complete text content, maintaining the original structure and formatting as much as possible.
Include all tables, lists, and structured data.
If there are multiple pages, separate them clearly."""
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([prompt, pdf_part])
            
            if response and response.text:
                print(f"DEBUG: Gemini extracted {len(response.text)} characters from PDF")
                return response.text
            
            return ""
            
        except Exception as e:
            print(f"ERROR: Gemini PDF extraction failed: {str(e)}")
            return ""

    def _extract_text_image_cloud_vision(self, image_file) -> str:
        """Extract text using Google Cloud Vision API with Pillow fallback"""
        try:
            # Try Cloud Vision first
            if self.vision_client:
                from google.cloud import vision
                
                image_bytes = image_file.getvalue()
                image = vision.Image(content=image_bytes)
                
                print(f"DEBUG: Cloud Vision API processing '{image_file.name}'...")
                response = self.vision_client.document_text_detection(image=image)
                
                if response.error.message:
                    raise Exception(response.error.message)
                
                if response.full_text_annotation:
                    extracted_text = response.full_text_annotation.text
                    print(f"DEBUG: Cloud Vision extracted {len(extracted_text)} characters")
                    return extracted_text
                else:
                    print(f"DEBUG: No text detected by Cloud Vision")
                    return ""
            
            # Fallback to Pillow if Vision client not available
            else:
                print(f"DEBUG: Using Pillow fallback for '{image_file.name}'...")
                return self._extract_text_image_pillow_fallback(image_file)
                
        except Exception as e:
            print(f"WARNING: Cloud Vision failed for '{image_file.name}': {str(e)}")
            print("DEBUG: Falling back to Pillow...")
            return self._extract_text_image_pillow_fallback(image_file)
    
    def _extract_text_image_pillow_fallback(self, image_file) -> str:
        """Fallback method using Pillow + Gemini for OCR"""
        try:
            from PIL import Image
            
            image_bytes = image_file.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            
            # Pillow can open/process images but can't extract text
            # Use Gemini as the fallback OCR method
            print(f"DEBUG: Using Pillow+Gemini fallback for '{image_file.name}'...")
            
            # Initialize Gemini if not already done
            if not hasattr(self, 'model') or self.model is None:
                genai.configure(api_key=Config._GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Simple OCR prompt for Gemini
            ocr_prompt = """Extract all text from this image accurately. 
            Return only the text content, preserving formatting and structure."""
            
            response = self.model.generate_content([ocr_prompt, image])
            extracted_text = response.text.strip()
            
            print(f"DEBUG: Pillow+Gemini fallback extracted {len(extracted_text)} characters")
            return extracted_text
                
        except Exception as e:
            print(f"ERROR: Pillow+Gemini fallback failed: {str(e)}")
            return f"[Failed to extract text from image: {image_file.name}]"


    def _extract_text_image_gemini_simple(self, image_file) -> str:
        """Gemini Vision with OCR-optimized prompting"""
        try:
            image_bytes = image_file.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            
            # Optimized OCR prompt for better accuracy
            ocr_prompt = """
            You are a professional OCR system. Extract ALL text from this image with perfect accuracy.
            
            CRITICAL REQUIREMENTS:
            1. Return ONLY the extracted text - no explanations or comments
            2. Preserve exact formatting, line breaks, and spacing
            3. Include every single word, number, and symbol visible
            4. Maintain proper paragraph structure
            5. If text is partially obscured, make your best interpretation
            6. Preserve document structure (headers, body text, lists, etc.)
            
            Extract the text now:
            """
            
            print(f"DEBUG: Gemini Simple OCR processing '{image_file.name}'...")
            response = self.model.generate_content([ocr_prompt, image])
            
            extracted_text = response.text.strip()
            print(f"DEBUG: Gemini Simple OCR extracted {len(extracted_text)} characters")
            
            return extracted_text
            
        except Exception as e:
            print(f"ERROR: Gemini Simple OCR failed for '{image_file.name}': {str(e)}")
            return ""

    def _extract_text_image_vision_rest(self, image_file) -> str:
        """Direct REST API call to Vision API (no SDK needed)"""
        try:
            import base64
            
            # Convert image to base64
            image_bytes = image_file.getvalue()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Vision API endpoint
            api_key = Config.GOOGLE_CLOUD_API_KEY  # Get from Google Cloud Console
            url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
            
            # Request payload
            payload = {
                "requests": [{
                    "image": {
                        "content": base64_image
                    },
                    "features": [{
                        "type": "DOCUMENT_TEXT_DETECTION",
                        "maxResults": 1
                    }]
                }]
            }
            
            print(f"DEBUG: Vision API REST call for '{image_file.name}'...")
            response = requests.post(url, json=payload)
            result = response.json()
            
            # Handle errors
            if 'error' in result:
                print(f"ERROR: Vision API error: {result['error']}")
                return ""
            
            # Extract text
            if (result.get('responses') and 
                result['responses'][0].get('fullTextAnnotation')):
                extracted_text = result['responses'][0]['fullTextAnnotation']['text']
                print(f"DEBUG: Vision API REST extracted {len(extracted_text)} characters")
                return extracted_text
            else:
                print(f"DEBUG: No text detected by Vision API REST")
                return ""
                
        except Exception as e:
            print(f"ERROR: Vision API REST failed: {str(e)}")
            return ""

    def _extract_text_image_gemini_original(self, image_file) -> str:
        """Your original Gemini implementation"""
        try:
            image_bytes = image_file.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            
            prompt = f"""
            You are an expert OCR system. Extract all text from this image accurately and completely.
            Preserve formatting, line breaks, structure, legal terminology, headers/footers, tables, lists. Note signatures.
            Image filename: {image_file.name}
            Return only the extracted text.
            """
            
            print(f"DEBUG: Calling Gemini Vision (original) for image '{image_file.name}'...")
            response = self.model.generate_content([prompt, image])
            
            extracted_text = response.text.strip()
            print(f"DEBUG: Gemini Vision (original) response for '{image_file.name}':\n{extracted_text[:500]}...")
            
            return extracted_text
            
        except Exception as e:
            print(f"ERROR: Gemini Vision (original) failed for '{image_file.name}': {str(e)}")
            return ""


    def _extract_text_image(self, image_file) -> str:
        """Extract text using the selected method"""
        method_map = {
            'cloud_vision': self._extract_text_image_cloud_vision,
            'gemini_simple': self._extract_text_image_gemini_simple,
            'vision_rest': self._extract_text_image_vision_rest,
            'gemini_original': self._extract_text_image_gemini_original
        }
        
        if self.ocr_method in method_map:
            return method_map[self.ocr_method](image_file)
        else:
            print(f"ERROR: Unknown OCR method: {self.ocr_method}")
            # Default to cloud_vision if method not found
            return self._extract_text_image_cloud_vision(image_file)

    # Rest of your methods remain the same...
    def extract_text_from_file(self, uploaded_file: Any) -> str:
        """Extract text from a single uploaded file"""
        if uploaded_file.type == "application/pdf":
            text = self._extract_text_pdf(uploaded_file)
        elif uploaded_file.type.startswith('image/'):
            text = self._extract_text_image(uploaded_file)
        elif uploaded_file.type == "text/plain":
            text = uploaded_file.getvalue().decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {uploaded_file.type}")
        
        # DO NOT anonymize here - anonymization happens at AI service level
        # Just track PII for reference if needed (reset=True for new document)
        if text and self.anonymizer:
            _, pii_mapping = self.anonymizer.anonymize(text, reset_mappings=True)
            self.pii_mapping.update(pii_mapping)
        
        return text  # Return original text with PII intact
    
    def get_pii_mapping(self) -> Dict[str, str]:
        """Get the PII mapping for extracted documents"""
        return self.pii_mapping
    
    def get_pii_summary(self) -> str:
        """Get a formatted summary of detected PII"""
        if self.anonymizer:
            return self.anonymizer.get_pii_summary()
        return "PII anonymization is disabled."
    
    def deanonymize_text(self, text: str) -> str:
        """Restore original PII in text"""
        if self.anonymizer and self.pii_mapping:
            return self.anonymizer.deanonymize(text, self.pii_mapping)
        return text
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess extracted text for analysis"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Trim
        text = text.strip()
        
        # Truncate if too long (based on config)
        max_length = Config.MAX_DOCUMENT_LENGTH
        if len(text) > max_length:
            print(f"WARNING: Text truncated from {len(text)} to {max_length} characters")
            text = text[:max_length] + "\n\n[Document truncated for processing...]"
        
        return text
    
    def validate_extracted_text(self, text: str) -> Tuple[bool, str]:
        """Validate that extracted text is meaningful"""
        if not text or len(text.strip()) == 0:
            return False, "No text content found"
        
        # Check minimum length
        min_length = Config.MIN_TEXT_FOR_ANALYSIS
        if len(text.strip()) < min_length:
            return False, f"Text too short (minimum {min_length} characters required)"
        
        # Check if text is mostly gibberish (very basic check)
        words = text.split()
        if len(words) < 5:
            return False, "Insufficient text content for analysis"
        
        # Check for reasonable character distribution
        alpha_chars = sum(c.isalpha() for c in text)
        if alpha_chars < len(text) * 0.3:  # At least 30% alphabetic characters
            return False, "Text appears to be corrupted or non-textual"
        
        return True, "Text is valid"
