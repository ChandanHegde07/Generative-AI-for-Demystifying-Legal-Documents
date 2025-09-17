import google.generativeai as genai
from typing import List, Dict, Any, Optional
from src.config import Config 
import re

class ChatService:
    def __init__(self):
        self.model = Config.initialize_gemini()
        self.conversation_history = []
        self.document_context = ""
        self.document_type = ""
        self.max_history_length = 20

    def set_document_context(self, document_text: str, doc_type: str):
        self.document_context = document_text
        self.document_type = doc_type
        self.conversation_history = []

    def _add_to_history(self, question: str, answer: str):
        self.conversation_history.extend([{"role": "user", "parts": [question]}, {"role": "model", "parts": [answer]}])
        self.conversation_history = self.conversation_history[-self.max_history_length:]

    def _build_conversation_context(self) -> str:
        return "\n".join([f"{entry['role'].capitalize()}: {entry['parts'][0]}" for entry in self.conversation_history])
    
    def _call_gemini_chat(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Chat API call failed: {str(e)}")

    def ask_question(self, question: str, language: str = "English") -> str:
        conversation_context = self._build_conversation_context()
        prompt = f"""
        You are an expert legal AI assistant.
        Document Type: {self.document_type}
        Document Content: {self.document_context}
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
        Document content: {self.document_context[:2000]}
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
        Document context: {self.document_context}
        Comparison question: {question}
        Provide a structured comparison in {language}: Options Analysis (Advantages, Disadvantages, Legal Implications, Costs/Benefits for each), Recommendation, Important Considerations.
        """
        return self._call_gemini_chat(prompt)