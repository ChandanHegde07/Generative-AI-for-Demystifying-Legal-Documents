# main.py - Updated for Gemini-only implementation
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import io
import PyPDF2
import pandas as pd

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-pro')

def extract_text_from_files(uploaded_files):
    """Extract text from uploaded files using Gemini Vision and PyPDF2"""
    combined_text = ""
    
    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.type == "application/pdf":
                # Handle PDF files with PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = ""
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text() + "\n"
                combined_text += f"\n--- Content from {uploaded_file.name} ---\n{pdf_text}\n"
            
            else:
                # Handle image files with Gemini Vision
                image_bytes = uploaded_file.getvalue()
                image = Image.open(io.BytesIO(image_bytes))
                
                prompt = f"""
                You are an expert at extracting text from legal documents.
                Extract all text from this legal document image from file: {uploaded_file.name}
                
                Pay special attention to:
                - Legal clauses and terms
                - Dates and deadlines
                - Party names and signatures
                - Important legal language
                - Contract terms and conditions
                - Compliance requirements
                
                Preserve the structure and formatting as much as possible.
                """
                
                response = model.generate_content([prompt, image])
                combined_text += f"\n--- Content from {uploaded_file.name} ---\n{response.text}\n"
                
        except Exception as e:
            combined_text += f"\n--- Error processing {uploaded_file.name}: {str(e)} ---\n"
    
    return combined_text.strip()

def detect_document_type(document_text):
    """Detect legal document type using Gemini"""
    prompt = f"""
    Analyze this legal document and classify it into one of these specific categories.
    Return only the category name, nothing else.
    
    Categories:
    - Contract Agreement
    - Legal Notice
    - Terms of Service
    - Privacy Policy
    - Employment Agreement
    - Lease Agreement
    - Insurance Policy
    - Healthcare Document
    - Government Legal Document
    - Court Document
    - Corporate Legal Document
    - Other Legal Document
    
    Document text (first 1000 characters): {document_text[:1000]}
    
    Based on the content, keywords, and structure, what type of legal document is this?
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "Legal Document"

def extract_key_entities(document_text, doc_type, language="English"):
    """Extract key entities and information from legal document"""
    prompt = f"""
    You are a legal document analysis expert. Extract key information from this {doc_type} and present it in {language}.
    
    Focus on extracting:
    - Parties involved (names, roles, addresses)
    - Important dates and deadlines
    - Financial amounts and payment terms
    - Key obligations and responsibilities
    - Rights and privileges
    - Termination clauses
    - Governing law and jurisdiction
    - Contact information
    - Signatures and execution details
    
    Document text: {document_text}
    
    Format the response with clear headings and bullet points for easy reading.
    Make it comprehensive but well-organized.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error extracting key entities: {str(e)}"

def generate_compliance_checklist(document_text, doc_type, language="English"):
    """Generate compliance checklist using Gemini"""
    prompt = f"""
    You are a legal compliance expert. Generate a detailed compliance checklist for this {doc_type} in {language}.
    
    Create a comprehensive checklist that includes:
    - Pre-execution requirements
    - Ongoing obligations during the agreement
    - Reporting and documentation requirements
    - Deadline-based actions
    - Compliance monitoring steps
    - Risk mitigation actions
    - Legal requirements to fulfill
    - Renewal or termination procedures
    
    Document text: {document_text}
    
    Format as a numbered checklist with:
    1. Clear action items
    2. Responsible parties
    3. Deadlines (if applicable)
    4. Priority levels (High/Medium/Low)
    
    Make it actionable and specific to this document.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating compliance checklist: {str(e)}"

def explain_complex_terms(document_text, doc_type, language="English"):
    """Explain complex legal terms using Gemini"""
    prompt = f"""
    You are a legal expert who explains complex terms in simple language.
    
    Analyze this {doc_type} and identify complex legal terms, then explain them in {language} using simple, everyday language that anyone can understand.
    
    For each complex term, provide:
    1. The term as it appears in the document
    2. A simple, clear explanation
    3. Why it's important in this context
    4. Any potential implications or risks
    
    Document text: {document_text}
    
    Focus on terms that would be confusing to someone without legal background.
    Format as: **Term:** Simple explanation with context.
    
    Make explanations practical and relevant to this specific document.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error explaining complex terms: {str(e)}"

def risk_assessment(document_text, doc_type, language="English"):
    """Perform legal risk assessment using Gemini"""
    prompt = f"""
    You are a legal risk assessment expert. Analyze this {doc_type} for potential legal risks, unfavorable terms, and areas of concern. Respond in {language}.
    
    Provide a comprehensive risk assessment covering:
    
    **HIGH RISK AREAS:**
    - Terms that could be legally problematic
    - Clauses that heavily favor one party
    - Potential financial liabilities
    - Unclear or ambiguous language
    - Missing important protections
    
    **MEDIUM RISK AREAS:**
    - Terms that need clarification
    - Potential future complications
    - Compliance challenges
    
    **LOW RISK AREAS:**
    - Standard terms and conditions
    - Well-balanced clauses
    
    **RECOMMENDATIONS:**
    - Suggested modifications or negotiations
    - Additional protections to consider
    - Legal advice recommendations
    
    Document text: {document_text}
    
    Be specific about which clauses or sections pose risks and explain why.
    Provide actionable recommendations for risk mitigation.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error performing risk assessment: {str(e)}"

def ask_gemini(user_input, document_text, language="English", doc_type="Legal Document"):
    """Handle user questions about the document using Gemini"""
    prompt = f"""
    You are an expert legal AI assistant. Answer this question about the {doc_type} in {language}.
    
    Be helpful, accurate, and explain legal concepts clearly. If the answer isn't directly in the document, 
    say so but provide general legal guidance if appropriate.
    
    Document context: {document_text}
    
    User question: {user_input}
    
    Provide a comprehensive, helpful answer based on the document content. 
    Use simple language and explain any legal terms you use.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"I apologize, but I encountered an error processing your question: {str(e)}"

def simplify_text(document_text, doc_type, language="English"):
    """Simplify legal text using Gemini"""
    prompt = f"""
    You are a legal writing expert who specializes in making complex legal documents understandable.
    
    Simplify this {doc_type} into plain {language} that anyone can understand.
    
    Guidelines:
    - Use simple, everyday words instead of legal jargon
    - Break down complex sentences into shorter ones
    - Explain what each section means in practical terms
    - Keep the essential meaning but make it accessible
    - Use bullet points and clear headings where helpful
    
    Document text: {document_text}
    
    Provide a simplified version that maintains accuracy but improves readability.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error simplifying text: {str(e)}"

def summarize_text(document_text, doc_type, language="English"):
    """Summarize legal document using Gemini"""
    prompt = f"""
    You are a legal document expert. Create a comprehensive summary of this {doc_type} in {language}.
    
    Your summary should include:
    - Main purpose and scope of the document
    - Key parties involved
    - Important terms and conditions
    - Critical dates and deadlines
    - Financial obligations and amounts
    - Rights and responsibilities of each party
    - Key risks or important clauses to note
    
    Document text: {document_text}
    
    Make the summary detailed enough to understand the document's key points without reading the full text.
    Use clear headings and bullet points for organization.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error summarizing document: {str(e)}"

def translate_text(text, target_language="English"):
    """Translate text using Gemini"""
    prompt = f"""
    Translate the following text to {target_language}.
    Maintain the legal accuracy and preserve the meaning.
    Keep legal terms appropriately translated with explanations if needed.
    
    Text to translate: {text}
    
    Provide an accurate translation that maintains the legal context.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error translating text: {str(e)}"