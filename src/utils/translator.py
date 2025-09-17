# src/utils/translator.py - Translation utilities using Gemini
import google.generativeai as genai
from typing import Dict, List, Optional
from src.config import Config

class GeminiTranslator:
    """Handles text translation using Gemini AI"""
    
    def __init__(self):
        """Initialize the translator with Gemini model"""
        self.model = Config.initialize_gemini()
        self.supported_languages = Config.SUPPORTED_LANGUAGES
    
    def translate_text(self, text: str, target_language: str, source_language: str = "English") -> str:
        """Translate text from source to target language"""
        try:
            if target_language == source_language:
                return text
            
            if target_language not in self.supported_languages:
                raise ValueError(f"Unsupported target language: {target_language}")
            
            prompt = f"""
            You are an expert translator specializing in legal documents.
            
            Translate the following text from {source_language} to {target_language}.
            
            Important guidelines:
            - Maintain legal accuracy and terminology
            - Preserve the formal tone and structure
            - Keep legal concepts consistent
            - If a legal term has no direct translation, provide the original term followed by explanation in brackets
            - Maintain formatting, line breaks, and structure
            - Do not translate proper names, addresses, or specific legal references
            
            Source text in {source_language}:
            {text}
            
            Provide only the translated text in {target_language}:
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Translation error: {str(e)}")
    
    def translate_legal_terms(self, terms: List[str], target_language: str) -> Dict[str, str]:
        """Translate specific legal terms with explanations"""
        try:
            if target_language not in self.supported_languages:
                raise ValueError(f"Unsupported target language: {target_language}")
            
            terms_text = "\n".join([f"- {term}" for term in terms])
            
            prompt = f"""
            You are a legal terminology expert. Translate these legal terms to {target_language} 
            and provide brief explanations for each term.
            
            Legal terms to translate:
            {terms_text}
            
            For each term, provide:
            1. Direct translation (if available)
            2. Brief explanation in {target_language}
            3. If no direct translation exists, explain the concept
            
            Format as:
            **English Term**: Translation - Explanation
            
            Respond in {target_language}:
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the response into a dictionary (simplified parsing)
            translations = {}
            lines = response.text.split('\n')
            
            for line in lines:
                if '**' in line and ':' in line:
                    try:
                        term_part = line.split('**')[1].split('**')[0]
                        translation_part = line.split(':', 1)[1].strip()
                        translations[term_part.strip()] = translation_part
                    except:
                        continue
            
            return translations
            
        except Exception as e:
            raise Exception(f"Legal terms translation error: {str(e)}")
    
    def get_language_summary(self, text: str, target_language: str) -> str:
        """Generate a summary in target language"""
        try:
            prompt = f"""
            Create a concise summary of this legal document in {target_language}.
            
            Focus on:
            - Main purpose of the document
            - Key parties involved
            - Important obligations and rights
            - Critical dates or deadlines
            - Key financial terms
            
            Document text:
            {text}
            
            Provide a clear, structured summary in {target_language}:
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Summary translation error: {str(e)}")
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        try:
            prompt = f"""
            Detect the primary language of this text. 
            Respond with only the language name in English (e.g., "English", "Hindi", "Kannada").
            
            Text to analyze:
            {text[:500]}
            
            Language:
            """
            
            response = self.model.generate_content(prompt)
            detected_language = response.text.strip()
            
            # Validate against supported languages
            if detected_language in self.supported_languages:
                return detected_language
            else:
                return "English"  # Default fallback
                
        except Exception as e:
            return "English"  # Default fallback on error
    
    def translate_with_context(self, text: str, target_language: str, context: str = "") -> str:
        """Translate text with additional context for better accuracy"""
        try:
            context_prompt = f" Context: {context}" if context else ""
            
            prompt = f"""
            You are translating a legal document.{context_prompt}
            
            Translate this text from English to {target_language}, maintaining legal accuracy:
            
            {text}
            
            Translation in {target_language}:
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Contextual translation error: {str(e)}")
    
    def is_translation_needed(self, text: str, target_language: str) -> bool:
        """Check if translation is needed"""
        if target_language == "English":
            return False
        
        detected_language = self.detect_language(text)
        return detected_language != target_language
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.supported_languages.copy()
    
    def validate_translation_quality(self, original: str, translated: str, target_language: str) -> Dict[str, any]:
        """Basic validation of translation quality"""
        try:
            # Simple heuristic checks
            original_words = len(original.split())
            translated_words = len(translated.split())
            
            # Word count ratio (translations can vary in length)
            word_ratio = translated_words / original_words if original_words > 0 else 0
            
            quality_score = "Good"
            issues = []
            
            # Check for potential issues
            if word_ratio < 0.3 or word_ratio > 3.0:
                quality_score = "Needs Review"
                issues.append("Significant length difference from original")
            
            if not translated.strip():
                quality_score = "Failed"
                issues.append("Empty translation")
            
            return {
                "quality_score": quality_score,
                "word_ratio": round(word_ratio, 2),
                "original_words": original_words,
                "translated_words": translated_words,
                "issues": issues,
                "target_language": target_language
            }
            
        except Exception as e:
            return {
                "quality_score": "Error",
                "error": str(e)
            }