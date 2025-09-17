# src/services/chat_service.py - Chat service for Gemini interaction
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from src.config import GEMINI_MODEL
from datetime import datetime

class ChatService:
    """Handles chat interactions with Gemini for legal document Q&A"""
    
    def __init__(self):
        """Initialize chat service with Gemini model"""
        # You may need to configure the API key here if not done globally
        # genai.configure(api_key="YOUR_API_KEY")
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.conversation_history = []
        self.document_context = ""
        self.document_type = ""
        self.max_history_length = 20  # Limit conversation history
    
    def set_document_context(self, document_text: str, doc_type: str):
        """Set the document context for the conversation"""
        self.document_context = document_text
        self.document_type = doc_type
        self.conversation_history = []  # Reset conversation when new document is loaded
    
    def ask_question(self, question: str, language: str = "English") -> str:
        """Process user question about the document"""
        try:
            # Build conversation context
            conversation_context = self._build_conversation_context()
            
            # Create comprehensive prompt
            prompt = f"""
            You are an expert legal AI assistant specializing in document analysis and legal guidance.
            
            **Document Context:**
            Document Type: {self.document_type}
            Document Content: {self.document_context}
            
            **Conversation History:**
            {conversation_context}
            
            **Current Question:** {question}
            **Response Language:** {language}
            
            **Instructions:**
            1. Analyze the question in the context of the provided document
            2. Provide a comprehensive, accurate answer in {language}
            3. Reference specific sections of the document when applicable
            4. Explain legal concepts in simple, understandable terms
            5. If the question cannot be answered from the document, clearly state this
            6. Provide practical guidance and implications
            7. Maintain conversational continuity with previous questions
            
            **Response Format:**
            - Start with a direct answer
            - Provide document-based evidence or references
            - Explain in simple terms
            - Include practical implications
            - Add warnings or cautions if relevant
            
            **Answer:**
            """
            
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            
            # Add to conversation history
            self._add_to_history(question, answer)
            
            return answer
            
        except Exception as e:
            error_message = f"I apologize, but I encountered an error processing your question: {str(e)}"
            self._add_to_history(question, error_message)
            return error_message
    
    def get_suggested_questions(self, language: str = "English") -> List[str]:
        """Generate suggested questions based on the document"""
        try:
            prompt = f"""
            Based on this {self.document_type}, suggest 8 relevant questions that users commonly ask.
            
            Document content: {self.document_context[:2000]}
            
            Generate questions in {language} that are:
            1. Specific to this document type
            2. Practical and actionable
            3. Cover different aspects (financial, legal, timeline, risks, etc.)
            4. Appropriate for non-lawyers to ask
            
            Return exactly 8 questions as a numbered list:
            1. [Question 1]
            2. [Question 2]
            ...
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the response to extract questions
            questions = []
            lines = response.text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering/bullets and clean up
                    question = line.split('.', 1)[-1].strip()
                    if len(question) > 10:  # Ensure it's a meaningful question
                        questions.append(question)
            
            return questions[:8]  # Ensure we return exactly 8 questions
            
        except Exception as e:
            # Fallback questions if generation fails
            return [
                "What are the main obligations of each party?",
                "What are the payment terms and deadlines?",
                "How can this agreement be terminated?",
                "What happens if someone breaches the contract?",
                "Are there any important deadlines I need to know?",
                "What are the potential risks in this agreement?",
                "Can this agreement be modified?",
                "What should I do next after signing?"
            ]
    
    def explain_document_section(self, section_text: str, language: str = "English") -> str:
        """Explain a specific section of the document"""
        try:
            prompt = f"""
            You are a legal expert explaining document sections to non-lawyers.
            
            Document Type: {self.document_type}
            Section to explain: {section_text}
            
            Provide an explanation in {language} that includes:
            
            1. **What This Section Says:** [Plain language summary]
            2. **Why It's Important:** [Significance and purpose]
            3. **Practical Impact:** [Real-world implications]
            4. **Key Terms Explained:** [Any complex terms defined simply]
            5. **Things to Watch Out For:** [Potential issues or concerns]
            6. **Related Sections:** [If applicable, mention related parts]
            
            Use simple, clear language and avoid legal jargon unless necessary.
            When you must use legal terms, explain them immediately.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Error explaining section: {str(e)}"
    
    def compare_options(self, question: str, language: str = "English") -> str:
        """Handle comparative questions about document options"""
        try:
            prompt = f"""
            You are analyzing options or alternatives related to this {self.document_type}.
            
            Document context: {self.document_context}
            
            Comparison question: {question}
            
            Provide a structured comparison in {language}:
            
            ## Options Analysis
            
            **Option 1:** [Description]
            - Advantages:
            - Disadvantages:
            - Legal implications:
            - Costs/Benefits:
            
            **Option 2:** [Description]
            - Advantages:
            - Disadvantages:
            - Legal implications:
            - Costs/Benefits:
            
            ## Recommendation
            Based on the document terms and general legal principles:
            [Provide balanced reasoning]
            
            ## Important Considerations
            - [Key factors to consider]
            - [Potential risks or benefits]
            - [Professional advice recommendations]
            
            Answer in {language} with clear, practical guidance.
            """
            
            response = self.model.generate_content(prompt)
        except Exception as e:
            return f"Error comparing options: {str(e)}"