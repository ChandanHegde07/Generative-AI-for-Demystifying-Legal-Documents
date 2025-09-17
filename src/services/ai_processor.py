import google.generativeai as genai
from typing import Dict, Any, Tuple, Optional
from src.config import Config
import json

class AIProcessor:
    def __init__(self):
        self.model = Config.initialize_gemini()

    def _call_gemini(self, system_instruction: str, content: str, doc_type: str = "", language: str = "English", json_output: bool = False, truncate_text_to: Optional[int] = None, image_data=None) -> Any:
        text_content = content[:truncate_text_to] if truncate_text_to else content
        
        full_prompt = f"""
        {system_instruction}
        
        Document Type: {doc_type}
        Document Text: {text_content}
        Response Language: {language}
        """
        
        try:
            if image_data:
                response = self.model.generate_content([full_prompt, image_data])
            else:
                response = self.model.generate_content(full_prompt)
            
            if json_output:
                return json.loads(response.text)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API call failed for {system_instruction.split('.')[0]}: {str(e)}")

    def classify_document(self, text: str) -> Dict[str, Any]:
        prompt_instruction = """
        You are a legal document classification expert. Analyze the provided document and provide its classification.
        Provide your analysis in this exact JSON format:
        {{"document_type": "one of: Contract Agreement, Legal Notice, Terms of Service, Privacy Policy, Employment Agreement, Lease Agreement, Insurance Policy, Healthcare Document, Government Legal Document, Court Document, Corporate Legal Document, Other Legal Document", "confidence": "High/Medium/Low", "key_indicators": ["list", "of", "key", "terms"], "document_structure": "Brief description", "estimated_complexity": "Simple/Moderate/Complex", "requires_legal_review": true/false}}
        """
        try:
            result = self._call_gemini(prompt_instruction, text, json_output=True, truncate_text_to=2000)
            return result
        except json.JSONDecodeError as e:
            return {"document_type": self._extract_document_type_fallback(str(e)), "confidence": "Medium", "key_indicators": [], "document_structure": "Could not parse structure", "estimated_complexity": "Moderate", "requires_legal_review": True}
        except Exception as e:
            return {"document_type": "Other Legal Document", "confidence": "Low", "error": str(e), "requires_legal_review": True}
    
    def extract_entities(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = """
        You are a legal document analysis expert. Extract comprehensive key information.
        Extract and organize: Parties, Financial Info, Dates, Key Terms, Legal Framework, Contact Info, Signatures.
        Present with bullet points and sections.
        """
        return self._call_gemini(instruction, text, doc_type, language)
    
    def perform_risk_analysis(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = """
        You are a legal risk assessment specialist. Perform a thorough risk analysis.
        Structure: 🔴 HIGH RISK, 🟡 MEDIUM RISK, 🟢 LOW RISK, 📋 MITIGATION RECOMMENDATIONS, ⚖️ LEGAL ADVICE.
        For each risk, explain: what, why problematic, consequences, recommended actions.
        """
        return self._call_gemini(instruction, text, doc_type, language)
    
    def generate_compliance_checklist(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = """
        You are a legal compliance expert. Generate a detailed compliance checklist.
        Organize by: PRE-EXECUTION, EXECUTION, ONGOING, PERIODIC REVIEW, DOCUMENTATION, BREACH MONITORING, AMENDMENT, TERMINATION.
        Specify for each: requirements, legal basis, consequences, best practices.
        """
        return self._call_gemini(instruction, text, doc_type, language)
    
    def explain_complex_terms(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = """
        You are a legal educator. Identify complex legal terms and explain them simply.
        For each term: Simple Definition, In This Context, Why It Matters, Example, Red Flags.
        Focus on jargon, contractual concepts, industry terms, rights/obligations.
        """
        return self._call_gemini(instruction, text, doc_type, language)
    
    def summarize_document(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = """
        You are a legal document expert. Create a comprehensive yet accessible summary.
        Structure: OVERVIEW, OBJECTIVES, PARTIES/RESPONSIBILITIES, FINANCIAL, DATES, LEGAL FRAMEWORK, RISKS, NEXT STEPS.
        Use clear, accessible language; highlight important points.
        """
        return self._call_gemini(instruction, text, doc_type, language)
    
    def simplify_document(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = f"""
        You are a legal writing expert. Rewrite this {doc_type} in {language} into plain, everyday language.
        Guidelines: replace jargon, shorter sentences, active voice, conversational tone, explain concepts, use "you", add explanations in [ ], clear headings.
        Example: "The party of the first part" → "You".
        Structure: What This Document Is About, Who Is Involved, What Each Person/Company Must Do, Dates, Money, What If Wrong, How to Change, Remember.
        """
        return self._call_gemini(instruction, text, doc_type, language)
    
    def answer_question(self, question: str, document_text: str, doc_type: str, language: str = "English") -> str:
        instruction = f"""
        You are a knowledgeable legal assistant. Answer the user question about their {doc_type}.
        Question: {question}
        Guidelines: Direct Answer, Document Reference, Explanation, Practical Implications, Additional Context, Warnings/Cautions.
        If not in document, state so, provide general guidance, suggest legal professional.
        """
        return self._call_gemini(instruction, document_text, doc_type, language)
    
    def _extract_document_type_fallback(self, response_text: str) -> str:
        doc_types = Config.SUPPORTED_DOCUMENT_TYPES 
        return next((dt for dt in doc_types if dt.lower() in response_text.lower()), "Other Legal Document")
    
    def validate_document_analysis(self, text: str) -> Tuple[bool, str]:
        if not text or len(text.strip()) < 100 or len(text.split()) < 50:
            return False, "Document too short or insufficient content."
        legal_indicators = ['agreement', 'contract', 'terms', 'conditions', 'party', 'clause', 'section']
        if not any(ind in text.lower() for ind in legal_indicators):
            return False, "Document may not be legal or text extraction poor."
        return True, "Document is suitable for analysis."