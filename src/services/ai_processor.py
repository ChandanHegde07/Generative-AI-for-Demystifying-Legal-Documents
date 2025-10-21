import google.generativeai as genai
from typing import Dict, Any, Tuple, Optional
from src.config import Config
from src.utils.pii_anonymizer import PIIAnonymizer
import json

class AIProcessor:
    def __init__(self):
        self.model = Config.initialize_gemini()
        self.anonymizer = PIIAnonymizer() if getattr(Config, 'ENABLE_PII_ANONYMIZATION', False) else None
        self.current_pii_mapping: Dict[str, str] = {}
    
    def reset_pii_mapping(self):
        """Reset PII mapping for a new document"""
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
            
            response_text = response.text
            if self.anonymizer and self.current_pii_mapping:
                response_text = self.anonymizer.deanonymize(response_text, self.current_pii_mapping)
            
            if json_output:
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    print(f"DEBUG: JSONDecodeError for prompt: {system_instruction}. Raw response: {response_text[:200]}...")
                    return {"error": "Failed to parse JSON response from AI. Raw output may be inconsistent.", "raw_response": response_text}
            return response_text
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
        if doc_type == "Healthcare Document":
            instruction = """
            You are a healthcare document analysis expert. Extract detailed information from the provided healthcare document, specifically a Medical Care Reimbursement Claim.
            Extract the following fields accurately. If a field is not present, use "N/A".
            Provide the output in a JSON format.
            JSON format should be:
            {{
                "Insured_Person_Details": {{"Name": "string", "IP_No": "string", "Employer": "string", "Wage_Period": "string"}},
                "Treatment_Details": {{"Hospital": "string", "Treatment_Date": "string (YYYY-MM-DD)", "Diagnosis": "string", "Admission_Type": "string"}},
                "Claim_Summary": {{"Consultation_Fee_Eligible_Amount": "float", "Consultation_Fee_Claimed_Amount": "float", "Consultation_Fee_Approved_Amount": "float", "Laboratory_Tests_Eligible_Amount": "float", "Laboratory_Tests_Claimed_Amount": "float", "Laboratory_Tests_Approved_Amount": "float", "Medicines_Eligible_Amount": "float", "Medicines_Claimed_Amount": "float", "Medicines_Approved_Amount": "float", "Injection_Administration_Eligible_Amount": "float", "Injection_Administration_Claimed_Amount": "float", "Injection_Administration_Approved_Amount": "float", "Total_Eligible_Amount": "float", "Total_Claimed_Amount": "float", "Total_Approved_Amount": "float", "Patient_Liability": "float"}},
                "Payment_Details": {{"Amount_Approved": "float", "Amount_Paid": "float", "Patient_Liability_Payment": "float", "Payment_Mode": "string", "UTR_No": "string", "Date_of_Payment": "string (YYYY-MM-DD)"}},
                "Deductions_Applied_Summary": ["bullet point summary of each deduction"],
                "Terms_And_Conditions_Summary": ["bullet point summary of each term and condition"]
            }}
            Ensure all float values are parsed as numbers. If a number is indicated by '*', do not include the '*' in the output.
            If a field is mentioned in the JSON schema but not found, set its value to "N/A".
            """
            try:
                extracted_data = self._call_gemini(instruction, text, doc_type, language, json_output=True)
                formatted_output = "### Extracted Key Information (Healthcare Document)\n\n"
                if "error" in extracted_data:
                    return f"**Error:** {extracted_data['error']}\n\n**Raw AI Response:**\n```json\n{extracted_data.get('raw_response', 'N/A')}\n```"
                for section, data in extracted_data.items():
                    formatted_output += f"**{section.replace('_', ' ')}:**\n"
                    if isinstance(data, dict):
                        for key, value in data.items():
                            formatted_output += f"- **{key.replace('_', ' ')}:** {value}\n"
                    elif isinstance(data, list):
                        for item in data:
                            formatted_output += f"- {item}\n"
                    formatted_output += "\n"
                return formatted_output
            except Exception as e:
                return f"An error occurred during healthcare document extraction: {str(e)}"
        else:
            instruction = """
            You are a legal document analysis expert. Extract comprehensive key information.
            Extract and organize: Parties, Financial Info, Dates, Key Terms, Legal Framework, Contact Info, Signatures.
            Present with bullet points and sections.
            """
            return self._call_gemini(instruction, text, doc_type, language)

    def perform_risk_analysis(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = "..."
        return self._call_gemini(instruction, text, doc_type, language)
    def generate_compliance_checklist(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = "..."
        return self._call_gemini(instruction, text, doc_type, language)
    def explain_complex_terms(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = "..."
        return self._call_gemini(instruction, text, doc_type, language)
    def summarize_document(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = "..."
        return self._call_gemini(instruction, text, doc_type, language)
    def simplify_document(self, text: str, doc_type: str, language: str = "English") -> str:
        instruction = "..."
        return self._call_gemini(instruction, text, doc_type, language)
    def answer_question(self, question: str, document_text: str, doc_type: str, language: str = "English") -> str:
        instruction = "..."
        return self._call_gemini(instruction, document_text, doc_type, language)
    def _extract_document_type_fallback(self, response_text: str) -> str:
        doc_types = Config.SUPPORTED_DOCUMENT_TYPES 
        return next((dt for dt in doc_types if dt.lower() in response_text.lower()), "Other Legal Document")
    def validate_document_analysis(self, text: str) -> Tuple[bool, str]:
        min_len = getattr(Config, 'MIN_TEXT_FOR_ANALYSIS', 50)
        if not text or len(text.strip()) < min_len: 
            return False, f"Document too short or insufficient content. Minimum {min_len} characters required."
        return True, "Document is suitable for analysis."

    def answer_question_with_rag(self, question: str, context: str, language: str = "English") -> str:
        """
        Answers a user's question using the context retrieved from the RAG system.
        This method sends a direct, clean prompt to the model and handles PII.
        """
        if not context or not context.strip():
            print("DEBUG: No context retrieved from RAG. Returning a direct message.")
            return f"I could not find any specific information about '{question}' in the document. Please try rephrasing your question."

        anonymized_question = question
        anonymized_context = context
        if self.anonymizer and getattr(Config, 'ENABLE_PII_ANONYMIZATION', False):
            print("DEBUG: Anonymizing inputs for RAG call.")
            anonymized_question, _ = self.anonymizer.anonymize(question)
            anonymized_context, _ = self.anonymizer.anonymize(context)

        prompt = f"""
        You are a highly intelligent legal assistant. Your task is to answer the user's question based *only* on the provided context from a document. Do not use any external knowledge. If the answer is not present in the context, state that clearly.

        **User's Question:**
        "{anonymized_question}"

        **Context from the Document:**
        ---
        {anonymized_context}
        ---

        **Instructions:**
        1.  Carefully analyze the "Context from the Document".
        2.  Formulate a direct and precise answer to the "User's Question" using only the information in the context.
        3.  If the context does not contain the information needed to answer the question, you MUST respond with: "Based on the provided sections of the document, I could not find an answer to your question."
        4.  Your entire response must be in the following language: {language}.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            final_response = response_text
            if self.anonymizer and self.current_pii_mapping:
                print("DEBUG: Deanonymizing RAG response.")
                final_response = self.anonymizer.deanonymize(response_text, self.current_pii_mapping)

            return final_response
            
        except Exception as e:
            error_message = f"An error occurred while communicating with the AI to answer the question: {str(e)}"
            print(f"ERROR: {error_message}")
            return error_message