import google.generativeai as genai
from typing import Dict, Any, Tuple, Optional, List
from src.config import Config
from src.utils.pii_anonymizer import PIIAnonymizer
import json
import re # <-- Added from your code

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
                # --- Your JSON cleaning logic is merged here ---
                cleaned_text = re.sub(r'```json\n?|```', '', response_text).strip()
                try:
                    return json.loads(cleaned_text)
                except json.JSONDecodeError:
                    # --- Your JSON repair logic is merged here ---
                    if cleaned_text.startswith('{') and cleaned_text.endswith('}'):
                        repaired_string = f"[{cleaned_text}]"
                        try:
                            json.loads(repaired_string)
                            return repaired_string
                        except json.JSONDecodeError:
                            pass # Fall through to error
                    
                    return {"error": "Failed to parse JSON response from AI.", "raw_response": cleaned_text}
            
            return response_text # Return plain text
        
        except Exception as e:
            # --- Pre-emptive Bug Fix ---
            error_msg = f"Error: The AI call failed. This can be due to safety settings or a network issue. (Details: {str(e)})"
            if json_output:
                return {"error": error_msg}
            return error_msg # Return error as string for UI

    def classify_document(self, text: str) -> Dict[str, Any]:
        # --- Your stricter JSON prompt ---
        instruction = """
        You are a document classification expert. Your response MUST be a single, clean JSON object with keys "document_type" and "confidence".
        Example: {"document_type": "Healthcare Document", "confidence": "High"}
        """
        return self._call_gemini(instruction, text, doc_type="", language="", json_output=True, truncate_text_to=2000)

    def extract_entities(self, text: str, doc_type: str, language: str = "English") -> str:
        # --- Your dashboard-ready prompt ---
        instruction = """
        You are a document analysis expert. Your response MUST be a single, clean JSON object. 
        The JSON should have top-level keys: "Parties", "Financials", "Key_Dates", and "Critical_Clauses".
        Each key should contain a dictionary of details. If a category is empty, return an empty dictionary for it.
        """
        # Return as JSON string, as app.py expects
        return json.dumps(self._call_gemini(instruction, text, doc_type, language, json_output=True))

    def perform_risk_analysis(self, text: str, doc_type: str, language: str = "English") -> str:
        # --- Your dashboard-ready prompt ---
        instruction = """
        You are a risk assessment specialist. Your response MUST be a single, clean JSON object.
        The JSON must have: "risk_score" (number 0-100), "risk_level" (string: "Low", "Medium", "High"), 
        "high_risk_clauses" (number), "medium_risk_clauses" (number), and "details" (a markdown string explaining risks).
        """
        return json.dumps(self._call_gemini(instruction, text, doc_type, language, json_output=True))
    
    def generate_compliance_checklist(self, text: str, doc_type: str, language: str = "English") -> str:
        # --- Your dashboard-ready prompt ---
        instruction = """
        You are a compliance expert. Your response MUST be a clean JSON list of objects.
        Each object must have "check" (string) and "status" (string: "Pass", "Fail", or "Review").
        """
        return json.dumps(self._call_gemini(instruction, text, doc_type, language, json_output=True))

    def get_summary(self, text: str, doc_type: str, language: str, summary_type: str) -> str:
        # --- Your summary function ---
        if summary_type == "key_points":
            instruction = "Extract the 5 most critical points from the document. Present them as a bulleted list."
        elif summary_type == "financial":
            instruction = "Summarize ONLY the financial aspects of this document, including coverage limits, costs, and payment details."
        elif summary_type == "executive":
            instruction = f"Provide a brief (max 3 sentences) executive summary of this {doc_type} for a busy professional, focusing on the most high-level impacts or agreements."
        elif summary_type == "concise":
            instruction = "Create a very short and direct, one-paragraph summary of the document, highlighting the main purpose and outcome."
        else: # Default to a detailed summary
            instruction = "Create a comprehensive yet accessible paragraph-style summary covering the main objectives, parties, and outcomes."
            
        return self._call_gemini(instruction, text, doc_type, language)

    def extract_financial_rules(self, text: str, doc_type: str, language: str = "English") -> str:
        # --- Your cost-sim function ---
        instruction = """
        You are an insurance expert. Extract ONLY key numerical financial rules. Your response MUST be a single, clean JSON object.
        All monetary values should be numbers only (e.g., 5000, not "Rs. 5,000").
        Keys: "deductible" (number), "co_payment_percentage" (number), "out_of_pocket_maximum" (number). Omit if not found.
        """
        return json.dumps(self._call_gemini(instruction, text, doc_type, language, json_output=True))

    def calculate_cost_liability(self, financial_rules: str, user_costs: str, doc_type: str, language: str = "English") -> str:
        # --- Your cost-sim function (with the strict prompt fix) ---
        instruction = f"""
        You are an expert insurance claims calculator for **India**.
        **CRITICAL: All currency MUST be in Indian Rupees (₹).** Do NOT use the dollar symbol ($).

        Your response MUST be a single, clean JSON object with these exact keys:
        1.  "total_bill" (number)
        2.  "insurance_pays" (number)
        3.  "user_pays" (number)
        4.  "explanation" (string)

        The "explanation" string MUST be a step-by-step markdown **bulleted list** (using `*`) in the {language} language.
        It must clearly show how you calculated the "user_pays" amount.

        ---
        EXAMPLE EXPLANATION:
        * Total Bill: ₹50,000.00
        * Policy Deductible: ₹0.00
        * Amount after Deductible: ₹50,000.00
        * User Co-payment (10%): ₹5,000.00
        * **Total User Pays:** ₹5,000.00
        * **Total Insurance Pays:** ₹45,000.00
        ---

        Now, perform this calculation:
        Policy Rules (in Rupees): {financial_rules}
        User Costs (in Rupees): {user_costs}
        """
        return json.dumps(self._call_gemini(instruction, "", doc_type, language, json_output=True))
    
    def generate_suggested_questions(self, text: str, doc_type: str, language: str = "English") -> str:
        # --- Friend's prompt (it's good) ---
        instruction = f'Based on the content from a {doc_type}, generate 3 concise, insightful questions a user might ask. Return ONLY a JSON list of strings, like: ["What is...?", "How does...?", "Why is...?"]'
        # Return as JSON string, as app.py expects
        return json.dumps(self._call_gemini(instruction, text, doc_type, language, json_output=True, truncate_text_to=4000))
    
    def explain_complex_terms(self, text: str, doc_type: str, language: str = "English") -> str:
        # --- Friend's prompt ---
        instruction = "You are a legal educator. Explain complex terms simply. For each: Definition, Context, Importance."
        return self._call_gemini(instruction, text, doc_type, language)

    def summarize_document(self, text: str, doc_type: str, language: str = "English") -> str:
        # --- Friend's generic summary prompt ---
        instruction = "You are a document expert. Create a comprehensive summary with sections: OVERVIEW, OBJECTIVES, etc."
        return self._call_gemini(instruction, text, doc_type, language)

    def simplify_document(self, text: str, doc_type: str, language: str = "English") -> str:
        # --- Friend's prompt ---
        instruction = f"Rewrite this {doc_type} in {language} into plain, everyday language."
        return self._call_gemini(instruction, text, doc_type, language)
    
    def answer_question_with_rag(self, question: str, context: str, language: str = "English") -> Dict[str, Any]:
        # --- Friend's critical RAG function ---
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
            # Direct call to model, as per friend's logic
            response_text = self.model.generate_content(prompt).text
            final_response = response_text
            if self.anonymizer and self.current_pii_mapping:
                final_response = self.anonymizer.deanonymize(response_text, self.current_pii_mapping)
            
            return {"answer": final_response, "context": context}
        except Exception as e:
            return {"answer": f"An error occurred: {e}", "context": context}