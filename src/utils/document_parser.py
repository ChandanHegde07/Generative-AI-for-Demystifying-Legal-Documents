# src/utils/document_parser.py - Document parsing utilities using Gemini
import google.generativeai as genai
from PIL import Image
import PyPDF2
import io
import os
from typing import List, Tuple, Optional
from src.config import Config

class DocumentParser:
    """Handles document parsing using Gemini AI and traditional methods"""
    
    def __init__(self):
        """Initialize the document parser"""
        self.model = Config.initialize_gemini()
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file using PyPDF2"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            extracted_text = ""
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():
                    extracted_text += f"\n--- Page {page_num} ---\n{page_text}\n"
            
            return extracted_text.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_from_image(self, image_file) -> str:
        """Extract text from image file using Gemini Vision"""
        try:
            # Read image bytes
            image_bytes = image_file.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            
            # Create prompt for Gemini Vision
            prompt = f"""
            You are an expert OCR system specialized in legal documents.
            Extract all text from this image accurately and completely.
            
            Instructions:
            - Preserve all text exactly as it appears
            - Maintain formatting, line breaks, and structure
            - Pay special attention to legal terminology
            - Include headers, footers, and any small text
            - Preserve tables, lists, and numbered items
            - Note any signatures, stamps, or handwritten annotations
            
            Image filename: {image_file.name}
            
            Return only the extracted text, preserving original formatting.
            """
            
            response = self.model.generate_content([prompt, image])
            return response.text
            
        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")
    
    def extract_from_multiple_files(self, uploaded_files) -> str:
        """Extract and combine text from multiple files"""
        combined_text = ""
        successful_files = []
        failed_files = []
        
        for uploaded_file in uploaded_files:
            try:
                # Validate file first
                is_valid, validation_message = Config.validate_file(uploaded_file)
                if not is_valid:
                    failed_files.append(f"{uploaded_file.name}: {validation_message}")
                    continue
                
                # Extract text based on file type
                if uploaded_file.type == "application/pdf":
                    extracted_text = self.extract_text_from_pdf(uploaded_file)
                else:
                    extracted_text = self.extract_text_from_image(uploaded_file)
                
                if extracted_text.strip():
                    combined_text += f"\n{'='*50}\n"
                    combined_text += f"DOCUMENT: {uploaded_file.name}\n"
                    combined_text += f"TYPE: {uploaded_file.type}\n"
                    combined_text += f"{'='*50}\n"
                    combined_text += extracted_text + "\n"
                    successful_files.append(uploaded_file.name)
                else:
                    failed_files.append(f"{uploaded_file.name}: No text extracted")
                    
            except Exception as e:
                failed_files.append(f"{uploaded_file.name}: {str(e)}")
        
        # Add processing summary
        if successful_files or failed_files:
            summary = f"\n{'='*50}\n"
            summary += f"PROCESSING SUMMARY\n"
            summary += f"{'='*50}\n"
            summary += f"Successfully processed: {len(successful_files)} files\n"
            if successful_files:
                summary += f"Success: {', '.join(successful_files)}\n"
            if failed_files:
                summary += f"Failed: {len(failed_files)} files\n"
                for failure in failed_files:
                    summary += f"  - {failure}\n"
            combined_text = summary + combined_text
        
        return combined_text.strip()
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        try:
            # Basic text cleaning
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Remove excessive whitespace
                cleaned_line = ' '.join(line.split())
                
                # Skip empty lines and very short lines that might be artifacts
                if len(cleaned_line) > 2:
                    cleaned_lines.append(cleaned_line)
            
            cleaned_text = '\n'.join(cleaned_lines)
            
            # Truncate if too long
            if len(cleaned_text) > Config.MAX_DOCUMENT_LENGTH:
                cleaned_text = cleaned_text[:Config.MAX_DOCUMENT_LENGTH] + "\n\n[Document truncated due to length...]"
            
            return cleaned_text
            
        except Exception as e:
            raise Exception(f"Error preprocessing text: {str(e)}")
    
    def extract_metadata(self, uploaded_file) -> dict:
        """Extract file metadata"""
        try:
            metadata = {
                'filename': uploaded_file.name,
                'file_type': uploaded_file.type,
                'file_size_bytes': len(uploaded_file.getvalue()),
                'file_size_mb': round(len(uploaded_file.getvalue()) / (1024 * 1024), 2)
            }
            
            # Add specific metadata based on file type
            if uploaded_file.type == "application/pdf":
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    metadata['num_pages'] = len(pdf_reader.pages)
                    
                    # Try to get PDF info if available
                    if pdf_reader.metadata:
                        metadata['pdf_title'] = pdf_reader.metadata.get('/Title', 'N/A')
                        metadata['pdf_author'] = pdf_reader.metadata.get('/Author', 'N/A')
                        metadata['pdf_creator'] = pdf_reader.metadata.get('/Creator', 'N/A')
                except:
                    metadata['num_pages'] = 'Unknown'
            
            elif uploaded_file.type.startswith('image/'):
                try:
                    image_bytes = uploaded_file.getvalue()
                    image = Image.open(io.BytesIO(image_bytes))
                    metadata['image_dimensions'] = f"{image.width}x{image.height}"
                    metadata['image_mode'] = image.mode
                    metadata['image_format'] = image.format
                except:
                    metadata['image_dimensions'] = 'Unknown'
            
            return metadata
            
        except Exception as e:
            return {'error': f"Could not extract metadata: {str(e)}"}
    
    def validate_extracted_text(self, text: str) -> Tuple[bool, str]:
        """Validate that extracted text is meaningful"""
        if not text or not text.strip():
            return False, "No text was extracted from the document"
        
        # Check for minimum meaningful content
        words = text.split()
        if len(words) < 10:
            return False, "Extracted text is too short to be meaningful"
        
        # Check for signs of successful OCR (presence of common legal words)
        legal_indicators = [
            'agreement', 'contract', 'party', 'clause', 'section',
            'terms', 'conditions', 'legal', 'law', 'court', 'rights',
            'obligations', 'liability', 'breach', 'notice', 'date'
        ]
        
        text_lower = text.lower()
        found_indicators = sum(1 for indicator in legal_indicators if indicator in text_lower)
        
        if found_indicators < 2:
            return False, "Text may not be a legal document or OCR quality is poor"
        
        return True, "Text extraction appears successful"