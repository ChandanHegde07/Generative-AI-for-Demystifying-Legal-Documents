import google.generativeai as genai
from typing import List, Dict, Any, Optional
import streamlit as st  
import re
import json # <-- Added import

from src.config import Config 
from src.utils.pii_anonymizer import PIIAnonymizer
from src.services.ai_processor import AIProcessor 

class ChatService:
    def __init__(self):
        self.ai_processor = AIProcessor() 
        self.conversation_history = []
        self.document_context = ""
        self.document_type = ""
        self.max_history_length = 20
    
    def reset_pii_mapping(self):
        """Tells the AI Processor to reset its PII mapping for a new document."""
        self.ai_processor.reset_pii_mapping()

    def set_document_context(self, document_text: str, doc_type: str):
        """Sets the context for the current chat session."""
        self.document_context = document_text
        self.document_type = doc_type
        self.conversation_history = [] # Reset history for the new document

    def _add_to_history(self, question: str, answer_dict: Dict[str, Any]):
        """
        Adds a question and answer pair to the conversation history.
        FIX: This now correctly handles the answer dictionary.
        """
        answer_text = answer_dict.get("answer", "No answer found.")
        self.conversation_history.extend([
            {"role": "user", "content": question}, 
            {"role": "ai", "content": answer_text} # Only add the text part to history
        ])
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]

    def ask_question(self, question: str, language: str = "English") -> Dict[str, Any]:
        """
        Answers a user's question using the RAG pipeline.
        FIX: This function now *always* returns a dictionary {"answer": "...", "context": "..."}
        """
        if not self.document_context:
            error_message = "Error: Document context not set. Please upload a document first."
            error_dict = {"answer": error_message, "context": None}
            self._add_to_history(question, error_dict)
            return error_dict

        try:
            rag_service = st.session_state.get("rag_service")
            if not rag_service:
                raise Exception("RAG service not found in session state. Please re-upload the document.")

            print(f"DEBUG: Retrieving context for question: '{question}'")
            context = rag_service.retrieve_relevant_chunks(question)

            # This calls the 'answer_question_with_rag' function we kept in ai_processor
            answer_dict = self.ai_processor.answer_question_with_rag(
                question=question,
                context=context,
                language=language
            )

            self._add_to_history(question, answer_dict)
            return answer_dict

        except Exception as e:
            error_message = f"Error processing your question: {str(e)}"
            error_dict = {"answer": error_message, "context": None}
            print(f"ERROR: {error_message}")
            self._add_to_history(question, error_dict)
            return error_dict

    def get_suggested_questions(self, language: str = "English") -> List[str]:
        """Generates suggested questions based on the full document context."""
        try:
            # This calls the function we merged into ai_processor
            questions_json_str = self.ai_processor.generate_suggested_questions(self.document_context, self.document_type, language)
            questions_list = json.loads(questions_json_str)
            return questions_list if isinstance(questions_list, list) else []
        except Exception as e:
            print(f"ERROR generating suggested questions: {e}")
            return [
                "What are the main obligations of each party?",
                "What are the payment terms and deadlines?",
                "How can this agreement be terminated?"
            ]
    
    def explain_document_section(self, section_text: str, language: str = "English") -> str:
        # This function isn't used in our merged app, but we keep it
        return self.ai_processor.explain_complex_terms(section_text, self.document_type, language)