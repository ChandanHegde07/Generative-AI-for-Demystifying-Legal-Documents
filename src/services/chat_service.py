import google.generativeai as genai
from typing import List, Dict, Any, Optional
from src.config import Config 
from src.utils.pii_anonymizer import PIIAnonymizer
import re

class ChatService:
    def __init__(self):
        self.model = Config.initialize_gemini()
        self.conversation_history = []
        self.document_context = ""
        self.document_context_anonymized = ""  # For Gemini
        self.document_type = ""
        self.max_history_length = 20
        self.anonymizer = PIIAnonymizer() if Config.ENABLE_PII_ANONYMIZATION else None
        self.current_pii_mapping: Dict[str, str] = {}
    
    def reset_pii_mapping(self):
        """Reset PII mapping for a new document"""
        self.current_pii_mapping = {}
        if self.anonymizer:
            self.anonymizer.pii_mapping = {}
            self.anonymizer.reverse_mapping = {}

    def set_document_context(self, document_text: str, doc_type: str):
        self.document_context = document_text  # Keep original
        self.document_type = doc_type
        self.conversation_history = []
        
        # Create anonymized version for Gemini if PII protection is enabled
        if self.anonymizer and Config.ENABLE_PII_ANONYMIZATION:
            self.document_context_anonymized, pii_mapping = self.anonymizer.anonymize(document_text)
            self.current_pii_mapping.update(pii_mapping)
        else:
            self.document_context_anonymized = document_text

    def _add_to_history(self, question: str, answer: str):
        self.conversation_history.extend([{"role": "user", "parts": [question]}, {"role": "model", "parts": [answer]}])
        self.conversation_history = self.conversation_history[-self.max_history_length:]

    def _build_conversation_context(self) -> str:
        return "\n".join([f"{entry['role'].capitalize()}: {entry['parts'][0]}" for entry in self.conversation_history])
    
    def _call_gemini_chat(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Deanonymize response to restore original PII
            if self.anonymizer and self.current_pii_mapping:
                response_text = self.anonymizer.deanonymize(response_text, self.current_pii_mapping)
            
            return response_text
        except Exception as e:
            raise Exception(f"Chat API call failed: {str(e)}")

    def ask_question(self, question: str, language: str = "English") -> str:
        conversation_context = self._build_conversation_context()
        prompt = f"""
        You are an expert legal AI assistant.
        Document Type: {self.document_type}
        Document Content: {self.document_context_anonymized}
        Conversation History: {conversation_context}
        Current Question: {question}
        Response Language: {language}
        Instructions: Analyze question, provide accurate answer in {language}, reference document, explain simply, state if not in document, provide guidance, maintain continuity.
        Response Format: Direct answer, document evidence, simple explanation, practical implications, warnings.
        Answer:
        """
        try:
            answer = self._call_gemini_chat(prompt)
            self._add_to_history(question, answer)
            return answer
        except Exception as e:
            error_message = f"Error processing question: {str(e)}"
            self._add_to_history(question, error_message)
            return error_message
    
    def get_suggested_questions(self, language: str = "English") -> List[str]:
        prompt = f"""
        Based on this {self.document_type}, suggest 8 relevant, practical, actionable questions for non-lawyers.
        Document content: {self.document_context_anonymized[:2000]}
        Generate questions in {language} as a numbered list.
        """
        try:
            response_text = self._call_gemini_chat(prompt)
            questions = [q.strip() for q in re.findall(r'^\s*\d+\.\s*(.+)', response_text, re.MULTILINE) if len(q.strip()) > 10]
            return questions[:8]
        except Exception:
            return [ 
                "What are the main obligations of each party?", "What are the payment terms and deadlines?",
                "How can this agreement be terminated?", "What happens if someone breaches the contract?",
                "Are there any important deadlines I need to know?", "What are the potential risks in this agreement?",
                "Can this agreement be modified?", "What should I do next after signing?"
            ]
    
    def explain_document_section(self, section_text: str, language: str = "English") -> str:
        prompt = f"""
        You are a legal expert explaining document sections to non-lawyers.
        Document Type: {self.document_type}
        Section to explain: {section_text}
        Provide explanation in {language} including: What it Says, Why Important, Practical Impact, Key Terms Explained, Things to Watch Out For, Related Sections.
        """
        return self._call_gemini_chat(prompt)
    
    def compare_options(self, question: str, language: str = "English") -> str:
        prompt = f"""
        You are analyzing options or alternatives related to this {self.document_type}.
        Document context: {self.document_context_anonymized}
        Comparison question: {question}
        Provide a structured comparison in {language}: Options Analysis (Advantages, Disadvantages, Legal Implications, Costs/Benefits for each), Recommendation, Important Considerations.
        """
        return self._call_gemini_chat(prompt)