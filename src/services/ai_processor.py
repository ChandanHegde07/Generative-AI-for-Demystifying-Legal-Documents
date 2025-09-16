from src.config import GEMINI_MODEL
from src.utils.translator import translate_text

def detect_document_type(text: str) -> str:
    prompt = f"""
    Analyze this document and classify it into one of these categories:
    - Legal Contract/Agreement
    - Medical Policy/Insurance
    - Terms of Service
    - Privacy Policy
    - Medical Report/Prescription
    - Government Document
    - Employment Document
    - Other Legal Document

    Document text: {text[:1000]}
    Respond with just the category name.
    """
    try:
        response = GEMINI_MODEL.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Document Classification (Error: {str(e)})"

def extract_key_entities(text: str, doc_type: str = "", language: str = "English") -> str:
    entity_prompts = {
        "Medical Policy": "Coverage Details, Premium Information, Deductibles, Exclusions, Claim Procedures, Network Providers, Policy Terms, Waiting Periods",
        "Medical Report": "Diagnosis, Medications, Procedures, Follow-up Instructions, Warning Signs, Lifestyle Advice",
        "Legal Contract": "Parties Involved, Contract Duration, Payment Terms, Obligations, Termination Clauses, Penalties, Governing Law"
    }
    # Original code used .split('/')[0] for doc_type to match the key
    base_prompt = entity_prompts.get(doc_type.split('/')[0], "Extract key information:")
    prompt = f"{base_prompt}\nDocument: {text[:4000]}\nFormat as markdown with headings."
    try:
        result = GEMINI_MODEL.generate_content(prompt).text.strip()
        # Original code used conditional translate, preserving that
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        return f"Key entity extraction failed: {str(e)}"

def generate_compliance_checklist(text: str, doc_type: str = "", language: str = "English") -> str:
    prompt = f"Create a practical compliance checklist for this {doc_type} document:\n{text[:4000]}\nFormat as numbered list."
    try:
        result = GEMINI_MODEL.generate_content(prompt).text.strip()
        # Original code used conditional translate, preserving that
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        return f"Checklist generation failed: {str(e)}"

def risk_assessment(text: str, doc_type: str = "", language: str = "English") -> str:
    prompt = f"Identify potential risks, concerns, or limitations in this {doc_type} document:\n{text[:4000]}"
    try:
        result = GEMINI_MODEL.generate_content(prompt).text.strip()
        # Original code used conditional translate, preserving that
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        return f"Risk assessment failed: {str(e)}"

def explain_complex_terms(text: str, doc_type: str = "", language: str = "English") -> str:
    prompt = f"Explain complex terms in this {doc_type} document in simple language:\n{text[:4000]}"
    try:
        result = GEMINI_MODEL.generate_content(prompt).text.strip()
        # Original code used conditional translate, preserving that
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        return f"Term explanation failed: {str(e)}"

def summarize_text(text: str, doc_type: str = "", language: str = "English") -> str:
    if not text:
        # Original code used conditional translate, preserving that
        return translate_text("No content to summarize.", language)
    prompt = f"Summarize this {doc_type} document with key points and action items:\n{text[:8000]}"
    try:
        result = GEMINI_MODEL.generate_content(prompt).text.strip()
        # Original code used conditional translate, preserving that
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        # Original code used conditional translate, preserving that
        return translate_text(f"Document summary failed: {str(e)}", language) if language != "English" else f"Document summary failed: {str(e)}"

def simplify_text(text: str, doc_type: str = "", language: str = "English") -> str:
    if not text:
        # Original code used conditional translate, preserving that
        return translate_text("No content to simplify.", language)
    prompt = f"Simplify this {doc_type} document into plain language:\n{text[:6000]}"
    try:
        result = GEMINI_MODEL.generate_content(prompt).text.strip()
        # Original code used conditional translate, preserving that
        return translate_text(result, language) if language != "English" else result
    except Exception as e:
        # Original code used conditional translate, preserving that
        return translate_text(f"Text simplification failed: {str(e)}", language) if language != "English" else f"Text simplification failed: {str(e)}"