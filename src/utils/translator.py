import google.generativeai as genai
from typing import Dict, List, Optional, Any
from src.config import Config 
import re 

class GeminiTranslator:
    def __init__(self):
        self.model = Config.initialize_gemini()
        self.supported_languages = Config.SUPPORTED_LANGUAGES
    
    def _call_gemini_translation(self, prompt: str, text_content: Optional[str] = None, image_data=None) -> str:
        try:
            if image_data:
                response = self.model.generate_content([prompt, image_data])
            elif text_content: 
                response = self.model.generate_content(f"{prompt}\n{text_content}")
            else: 
                response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Gemini API call failed for translation: {str(e)}")

    def translate_text(self, text: str, target_language: str, source_language: str = "English") -> str:
        if target_language == source_language: return text
        if target_language not in self.supported_languages:
            raise ValueError(f"Unsupported target language: {target_language}")
        
        prompt = f"""
        You are an expert translator specializing in legal documents.
        Translate the following text from {source_language} to {target_language}.
        Guidelines: maintain legal accuracy/terminology, formal tone, consistent legal concepts, explain untranslatable terms, preserve formatting, do not translate proper names/addresses/references.
        Source text in {source_language}:
        {text}
        Provide only the translated text in {target_language}:
        """
        return self._call_gemini_translation(prompt)
    
    def translate_legal_terms(self, terms: List[str], target_language: str) -> Dict[str, str]:
        if target_language not in self.supported_languages:
            raise ValueError(f"Unsupported target language: {target_language}")
        
        terms_text = "\n".join([f"- {term}" for term in terms])
        prompt = f"""
        You are a legal terminology expert. Translate these legal terms to {target_language} and provide brief explanations.
        Legal terms to translate:
        {terms_text}
        For each term, provide: 1. Direct translation (if available) 2. Brief explanation in {target_language} 3. If no direct translation, explain the concept.
        Format as: **English Term**: Translation - Explanation
        Respond in {target_language}:
        """
        response_text = self._call_gemini_translation(prompt)
        
        translations = {}
        pattern = re.compile(r'\*\*(.*?)\*\*\s*:\s*(.*)')
        for line in response_text.split('\n'):
            match = pattern.match(line)
            if match:
                english_term = match.group(1).strip()
                translation_explanation = match.group(2).strip()
                translations[english_term] = translation_explanation
        return translations
            
    def get_language_summary(self, text: str, target_language: str) -> str:
        prompt = f"""
        Create a concise summary of this legal document in {target_language}.
        Focus on: Main purpose, Key parties, Important obligations/rights, Critical dates/deadlines, Key financial terms.
        Document text:
        {text}
        Provide a clear, structured summary in {target_language}:
        """
        return self._call_gemini_translation(prompt)
    
    def detect_language(self, text: str) -> str:
        prompt = f"""
        Detect the primary language of this text. Respond with only the language name in English (e.g., "English", "Hindi").
        Text to analyze:
        {text[:500]}
        Language:
        """
        try:
            detected_language = self._call_gemini_translation(prompt)
            return detected_language if detected_language in self.supported_languages else "English"
        except Exception: 
            return "English"
    
    def translate_with_context(self, text: str, target_language: str, context: str = "") -> str:
        context_prompt = f" Context: {context}" if context else ""
        prompt = f"""
        You are translating a legal document.{context_prompt}
        Translate this text from English to {target_language}, maintaining legal accuracy:
        {text}
        Translation in {target_language}:
        """
        return self._call_gemini_translation(prompt)
    
    def is_translation_needed(self, text: str, target_language: str) -> bool:
        if target_language == "English":
            return False
        return self.detect_language(text) != target_language
    
    def get_supported_languages(self) -> List[str]:
        return self.supported_languages.copy()
    
    def validate_translation_quality(self, original: str, translated: str, target_language: str) -> Dict[str, Any]:
        try:
            original_words = len(original.split())
            translated_words = len(translated.split())
            
            word_ratio = translated_words / original_words if original_words > 0 else (1.0 if translated_words == 0 else float('inf'))
            
            quality_score, issues = "Good", []
            
            if not translated.strip():
                quality_score, issues = "Failed", ["Empty translation"]
            elif original_words == 0 and translated_words > 0:
                quality_score, issues = "Needs Review", ["Translated content present but original was empty"]
            elif word_ratio < 0.3 or word_ratio > 3.0:
                quality_score, issues = "Needs Review", ["Significant length difference from original"]
            
            return {
                "quality_score": quality_score,
                "word_ratio": round(word_ratio, 2),
                "original_words": original_words,
                "translated_words": translated_words,
                "issues": issues,
                "target_language": target_language
            }
        except Exception as e:
            return {"quality_score": "Error", "error": str(e)}