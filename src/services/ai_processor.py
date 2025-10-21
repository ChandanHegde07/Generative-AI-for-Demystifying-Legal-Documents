import google.generativeai as genai
from typing import Dict, Any, Tuple, Optional, List 
from src.config import Config
from src.utils.pii_anonymizer import PIIAnonymizer
import json

class AIProcessor:
    def __init__(self):
        self.model = Config.initialize_gemini()
        self.anonymizer = PIIAnonymizer() if getattr(Config, 'ENABLE_PII_ANONYMIZATION', False) else None
        self.current_pii_mapping: Dict[str, str] = {}
    
    def reset_pii_mapping(self):
        self.current_pii_mapping = {}
        if self.anonymizer:
            self.anonymizer.pii_mapping = {}
            self.anonymizer.reverse_mapping = {}

    def _call_gemini(self, system_instruction: str, content: str, doc_type: str = "", language: str = "English", json_output: bool = False, truncate_text_to: Optional[int] = None, image_data=None) -> Any:
        text_content = content[:truncate_text_to] if truncate_text_to else content
        
        pii_mapping = {}
        if self.anonymizer and getattr(Config, 'ENABLE_PII_ANONYMIZATION', False):
            text_content, pii_mapping = self.anonymizer.anonymize(text_content)
            self.current_pii_mapping = {**self.current_pii_mapping, **pii_mapping}
        
        full_prompt = f"{system_instruction}\n\nDocument Type: {doc_type}\nDocument Text: {text_content}\nResponse Language: {language}"
        
        try:
            response = self.model.generate_content([full_prompt, image_data] if image_data else full_prompt)
            response_text = response.text
            if self.anonymizer and self.current_pii_mapping:
                response_text = self.anonymizer.deanonymize(response_text, self.current_pii_mapping)
            
            if json_output:
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    return {"error": "Failed to parse JSON response from AI.", "raw_response": response_text}
            return response_text
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")

    def classify_document(self, text: str) -> Dict[str, Any]:
        instruction = 'You are a document classification expert. Analyze the text. Provide a JSON analysis: {{"document_type": "...", "confidence": "...", ...}}'
        return self._call_gemini(instruction, text, json_output=True, truncate_text_to=2000)

    def extract_entities(self, text: str, doc_type: str, language: str = "English") -> str:
        if doc_type == "Healthcare Document":
            instruction = 'You are a healthcare expert. Extract info from the claim into this JSON format: {{"Insured_Person_Details": {...}, ...}}'
            try:
                data = self._call_gemini(instruction, text, doc_type, language, json_output=True)
                if "error" in data: return f"**Error:** {data['error']}\n\n**Raw Response:**\n```\n{data.get('raw_response', 'N/A')}\n```"
                output = "### Extracted Key Information\n\n"
                for section, details in data.items():
                    output += f"**{section.replace('_', ' ')}:**\n"
                    if isinstance(details, dict):
                        for key, value in details.items(): output += f"- **{key.replace('_', ' ')}:** {value}\n"
                    elif isinstance(details, list):
                        for item in details: output += f"- {item}\n"
                    output += "\n"
                return output
            except Exception as e: return f"An error occurred: {e}"
        else:
            instruction = "You are a legal expert. Extract key info like Parties, Dates, and Financials. Present with sections and bullets."
            return self._call_gemini(instruction, text, doc_type, language)

    def perform_risk_analysis(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = "You are a risk specialist. Analyze for risks. Structure: HIGH, MEDIUM, LOW RISK, MITIGATION."
        return self._call_gemini(instruction, text, doc_type, language)

    def generate_compliance_checklist(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = "You are a compliance expert. Generate a checklist organized by lifecycle stage (e.g., PRE-EXECUTION)."
        return self._call_gemini(instruction, text, doc_type, language)

    def explain_complex_terms(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = "You are a legal educator. Explain complex terms simply. For each: Definition, Context, Importance."
        return self._call_gemini(instruction, text, doc_type, language)

    def summarize_document(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = "You are a document expert. Create a comprehensive summary with sections: OVERVIEW, OBJECTIVES, etc."
        return self._call_gemini(instruction, text, doc_type, language)

    def simplify_document(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = f"Rewrite this {doc_type} in {language} into plain, everyday language."
        return self._call_gemini(instruction, text, doc_type, language)
    
    def answer_question_with_rag(self, question: str, context: str, language: str = "English") -> Dict[str, Any]:
        if not context or not context.strip():
            return {"answer": f"I could not find any specific information about '{question}' in the document. Please try rephrasing your question.", "context": None}

        anonymized_question, anonymized_context = question, context
        if self.anonymizer and getattr(Config, 'ENABLE_PII_ANONYMIZATION', False):
            anonymized_question, _ = self.anonymizer.anonymize(question)
            anonymized_context, _ = self.anonymizer.anonymize(context)

        prompt = f"""You are an assistant. Answer the user's question based ONLY on the provided context. If the answer is not in the context, state that clearly.
        User's Question: "{anonymized_question}"
        Context: --- {anonymized_context} ---
        Instructions: Formulate a direct answer using only the context. Respond in {language}."""
        
        try:
            response_text = self.model.generate_content(prompt).text
            final_response = response_text
            if self.anonymizer and self.current_pii_mapping:
                final_response = self.anonymizer.deanonymize(response_text, self.current_pii_mapping)
            
            return {"answer": final_response, "context": context}
        except Exception as e:
            return {"answer": f"An error occurred: {e}", "context": context}

    def generate_suggested_questions(self, text: str, doc_type: str, language: str = "English") -> List[str]:
        instruction = f'Based on the content from a {doc_type}, generate 3 concise, insightful questions a user might ask. Return ONLY a JSON list of strings, like: ["What is...?", "How does...?", "Why is...?"]'
        try:
            result = self._call_gemini(instruction, text, doc_type, language, json_output=True, truncate_text_to=4000)
            return result if isinstance(result, list) else []
        except Exception as e:
            print(f"ERROR generating suggested questions: {e}")
            return []
