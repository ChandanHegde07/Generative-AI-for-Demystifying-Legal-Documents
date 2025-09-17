# src/services/ai_processor.py - Core AI processing service using Gemini
import google.generativeai as genai
from typing import Dict, List, Any, Optional, Tuple
from src.config import Config
import json
import re

class AIProcessor:
    """Core AI processing service using Gemini for all legal document analysis"""
    
    def __init__(self):
        """Initialize AI processor with Gemini model"""
        self.model = Config.initialize_gemini()
        self.model_settings = Config.get_model_settings()
    
    def classify_document(self, text: str) -> Dict[str, Any]:
        """Classify document type and extract basic metadata"""
        try:
            prompt = f"""
            You are a legal document classification expert. Analyze this document and provide classification.
            
            Document text: {text[:2000]}
            
            Provide your analysis in this exact JSON format:
            {{
                "document_type": "one of: Contract Agreement, Legal Notice, Terms of Service, Privacy Policy, Employment Agreement, Lease Agreement, Insurance Policy, Healthcare Document, Government Legal Document, Court Document, Corporate Legal Document, Other Legal Document",
                "confidence": "High/Medium/Low",
                "key_indicators": ["list", "of", "key", "terms", "that", "led", "to", "classification"],
                "document_structure": "Brief description of document structure",
                "estimated_complexity": "Simple/Moderate/Complex",
                "requires_legal_review": true/false
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                # Try to parse JSON response
                result = json.loads(response.text)
                return result
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "document_type": self._extract_document_type_fallback(response.text),
                    "confidence": "Medium",
                    "key_indicators": [],
                    "document_structure": "Could not parse structure",
                    "estimated_complexity": "Moderate",
                    "requires_legal_review": True
                }
                
        except Exception as e:
            return {
                "document_type": "Other Legal Document",
                "confidence": "Low",
                "error": str(e),
                "requires_legal_review": True
            }
    
    def extract_entities(self, text: str, doc_type: str, language: str = "English") -> str:
        """Extract key entities and information from document"""
        try:
            prompt = f"""
            You are a legal document analysis expert. Extract comprehensive key information from this {doc_type} in {language}.
            
            Document text: {text}
            
            Extract and organize the following information:
            
            ## PARTIES INVOLVED
            - Names, roles, and addresses of all parties
            - Corporate entities, individuals, and their relationships
            
            ## FINANCIAL INFORMATION
            - All monetary amounts, payment terms, and schedules
            - Currency, interest rates, penalties, and financial obligations
            
            ## DATES AND DEADLINES
            - Execution dates, effective dates, expiration dates
            - Payment due dates, milestone dates, and renewal dates
            
            ## KEY TERMS AND CONDITIONS
            - Primary obligations of each party
            - Rights, privileges, and restrictions
            - Performance criteria and deliverables
            
            ## LEGAL FRAMEWORK
            - Governing law and jurisdiction
            - Dispute resolution mechanisms
            - Termination and breach conditions
            
            ## CONTACT INFORMATION
            - Addresses, phone numbers, email addresses
            - Legal representatives and authorized contacts
            
            ## SIGNATURES AND EXECUTION
            - Signature requirements and execution details
            - Witness requirements and notarization
            
            Present the information in a clear, organized format with bullet points and sections.
            Focus on practical, actionable information that would be important to the parties involved.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error extracting entities: {str(e)}"
    
    def perform_risk_analysis(self, text: str, doc_type: str, language: str = "English") -> str:
        """Perform comprehensive risk analysis of the document"""
        try:
            prompt = f"""
            You are a legal risk assessment specialist. Perform a thorough risk analysis of this {doc_type} in {language}.
            
            Document text: {text}
            
            Provide a comprehensive risk assessment with the following structure:
            
            ## 🔴 HIGH RISK AREAS
            Identify and analyze:
            - Clauses that create significant liability exposure
            - Terms that heavily favor one party over another
            - Ambiguous language that could lead to disputes
            - Missing essential protections or safeguards
            - Potential regulatory or compliance violations
            - Financial risks and unlimited liability exposures
            
            ## 🟡 MEDIUM RISK AREAS
            Analyze:
            - Terms that may need clarification or modification
            - Potential operational challenges or complications
            - Areas where additional protections might be beneficial
            - Timeline or performance risks
            
            ## 🟢 LOW RISK AREAS
            Note:
            - Well-balanced and standard terms
            - Appropriate protections and safeguards
            - Clear and unambiguous language
            
            ## 📋 RISK MITIGATION RECOMMENDATIONS
            Provide specific, actionable recommendations:
            - Suggested contract modifications or additions
            - Negotiation points to address
            - Additional legal protections to consider
            - Due diligence recommendations
            
            ## ⚖️ LEGAL ADVICE RECOMMENDATIONS
            - Areas requiring specialized legal counsel
            - Regulatory compliance considerations
            - Industry-specific risk factors
            
            For each risk identified, explain:
            1. What the risk is
            2. Why it's problematic
            3. Potential consequences
            4. Recommended actions
            
            Be specific about clause references and provide practical guidance.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error performing risk analysis: {str(e)}"
    
    def generate_compliance_checklist(self, text: str, doc_type: str, language: str = "English") -> str:
        """Generate detailed compliance checklist"""
        try:
            prompt = f"""
            You are a legal compliance expert. Create a comprehensive compliance checklist for this {doc_type} in {language}.
            
            Document text: {text}
            
            Generate a detailed, actionable compliance checklist organized by phases:
            
            ## 📋 PRE-EXECUTION COMPLIANCE
            Tasks to complete before signing:
            □ Task description - Responsible party - Deadline/Timeline - Priority (High/Medium/Low)
            
            ## 🚀 EXECUTION REQUIREMENTS
            Requirements for proper document execution:
            □ Task description - Responsible party - Legal requirements - Priority
            
            ## 📊 ONGOING COMPLIANCE OBLIGATIONS
            Regular obligations during the agreement term:
            □ Task description - Frequency - Responsible party - Consequences of non-compliance
            
            ## 📅 PERIODIC REVIEW REQUIREMENTS
            Scheduled reviews and renewals:
            □ Task description - Review frequency - Key focus areas - Responsible party
            
            ## 📝 DOCUMENTATION AND RECORD-KEEPING
            Required documentation and retention:
            □ Document type - Retention period - Storage requirements - Access controls
            
            ## ⚠️ BREACH AND DEFAULT MONITORING
            Monitoring for potential violations:
            □ Risk area - Monitoring frequency - Warning signs - Escalation procedures
            
            ## 🔄 AMENDMENT AND MODIFICATION PROCEDURES
            Process for making changes:
            □ Amendment type - Approval required - Documentation needed - Timeline
            
            ## 🏁 TERMINATION AND WIND-DOWN
            End-of-agreement compliance:
            □ Task description - Timing - Responsible party - Legal implications
            
            For each item, specify:
            - Exact requirements from the document
            - Legal or regulatory basis
            - Consequences of non-compliance
            - Best practices for implementation
            
            Make the checklist specific to this document's requirements and practical for implementation.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating compliance checklist: {str(e)}"
    
    def explain_complex_terms(self, text: str, doc_type: str, language: str = "English") -> str:
        """Explain complex legal terms in simple language"""
        try:
            prompt = f"""
            You are a legal educator who specializes in making complex legal concepts understandable to non-lawyers.
            
            Analyze this {doc_type} and identify complex legal terms, then explain them in {language} using simple, clear language.
            
            Document text: {text}
            
            For each complex term found, provide:
            
            ## 📚 LEGAL TERMS EXPLAINED
            
            **[Legal Term as it appears in document]**
            - **Simple Definition:** [Clear, everyday language explanation]
            - **In This Context:** [What it means specifically in this document]
            - **Why It Matters:** [Practical implications for the parties]
            - **Example:** [Real-world example if helpful]
            - **Red Flags:** [Potential issues or things to watch out for]
            
            Focus on terms that would be confusing or intimidating to someone without legal training.
            
            Include terms such as:
            - Legal jargon and Latin phrases
            - Complex contractual concepts
            - Industry-specific terminology
            - Procedural and technical terms
            - Rights, obligations, and liability concepts
            
            Make explanations:
            - Clear and conversational
            - Practical and relevant
            - Free of additional legal jargon
            - Focused on real-world implications
            
            If a term has multiple meanings, explain the specific meaning in this document's context.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error explaining complex terms: {str(e)}"
    
    def summarize_document(self, text: str, doc_type: str, language: str = "English") -> str:
        """Create comprehensive document summary"""
        try:
            prompt = f"""
            You are a legal document expert. Create a comprehensive yet accessible summary of this {doc_type} in {language}.
            
            Document text: {text}
            
            Structure your summary as follows:
            
            ## 📄 DOCUMENT OVERVIEW
            - Document type and purpose
            - Execution date and effective period
            - Key parties involved and their roles
            
            ## 🎯 MAIN OBJECTIVES
            - Primary purpose of the agreement
            - What each party hopes to achieve
            - Overall scope and limitations
            
            ## 👥 PARTIES AND RESPONSIBILITIES
            For each party, summarize:
            - Who they are (name, role, capacity)
            - Their main obligations and duties
            - Their rights and benefits
            - Key performance requirements
            
            ## 💰 FINANCIAL TERMS
            - All monetary amounts and payment terms
            - Payment schedules and methods
            - Penalties, interest, and additional costs
            - Financial guarantees or security
            
            ## 📅 IMPORTANT DATES AND TIMELINES
            - Start and end dates
            - Key milestones and deadlines
            - Renewal or termination dates
            - Notice periods required
            
            ## ⚖️ LEGAL FRAMEWORK
            - Governing law and jurisdiction
            - How disputes will be resolved
            - Termination conditions and procedures
            - Amendment and modification process
            
            ## ⚠️ KEY RISKS AND CONSIDERATIONS
            - Important limitations or exclusions
            - Potential areas of concern
            - Recommendations for the parties
            
            ## 📞 NEXT STEPS
            - What needs to happen next
            - Who needs to take action and when
            - Any immediate requirements
            
            Write in clear, accessible language that someone without legal training can understand.
            Focus on practical implications and actionable information.
            Highlight the most important points that could affect the parties.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error summarizing document: {str(e)}"
    
    def simplify_document(self, text: str, doc_type: str, language: str = "English") -> str:
        """Simplify complex legal language into plain language"""
        try:
            prompt = f"""
            You are a legal writing expert who specializes in translating "legalese" into plain, everyday language.
            
            Rewrite this {doc_type} in {language} using simple, clear language that anyone can understand.
            
            Original document text: {text}
            
            Guidelines for simplification:
            1. Replace complex legal terms with simple equivalents
            2. Break long, complicated sentences into shorter ones
            3. Use active voice instead of passive voice when possible
            4. Replace formal language with conversational tone
            5. Explain concepts rather than just stating rules
            6. Use "you" and "your" to make it personal
            7. Add explanations in brackets [ ] when technical terms must be kept
            8. Organize information with clear headings and bullet points
            
            Example transformations:
            - "The party of the first part" → "You" or "[Company name]"
            - "Shall be deemed to have" → "Will be considered to have"
            - "In the event that" → "If"
            - "Notwithstanding" → "Despite" or "Even though"
            - "Pursuant to" → "According to" or "Following"
            
            Structure the simplified version with:
            ## What This Document Is About
            ## Who Is Involved
            ## What Each Person/Company Must Do
            ## Important Dates and Deadlines
            ## Money and Payments
            ## What Happens If Something Goes Wrong
            ## How to Make Changes
            ## Important Things to Remember
            
            Keep all the essential legal meaning but make it accessible to someone with an 8th-grade reading level.
            When you must use a legal term, immediately explain what it means in plain language.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error simplifying document: {str(e)}"
    
    def answer_question(self, question: str, document_text: str, doc_type: str, language: str = "English") -> str:
        """Answer specific questions about the document"""
        try:
            prompt = f"""
            You are a knowledgeable legal assistant helping someone understand their {doc_type}.
            
            Document context: {document_text}
            
            User question: {question}
            
            Please answer in {language} following these guidelines:
            
            1. **Direct Answer**: Start with a clear, direct answer to the question
            2. **Document Reference**: Quote or reference the specific part of the document that supports your answer
            3. **Explanation**: Explain the concept in simple terms
            4. **Practical Implications**: What does this mean in real-world terms?
            5. **Additional Context**: Any related information that would be helpful
            6. **Warnings/Cautions**: Any potential issues or things to be aware of
            
            If the answer isn't clearly stated in the document:
            - Say so honestly
            - Provide general legal guidance if appropriate
            - Suggest consulting with a legal professional for specific advice
            
            Use a helpful, conversational tone and avoid legal jargon unless necessary.
            When you must use legal terms, explain them immediately.
            
            Structure your response clearly with headings if the answer is complex.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
    
    def _extract_document_type_fallback(self, response_text: str) -> str:
        """Fallback method to extract document type from response"""
        doc_types = Config.SUPPORTED_DOCUMENT_TYPES
        response_lower = response_text.lower()
        
        for doc_type in doc_types:
            if doc_type.lower() in response_lower:
                return doc_type
        
        return "Other Legal Document"
    
    def validate_document_analysis(self, text: str) -> Tuple[bool, str]:
        """Validate that the document is suitable for analysis"""
        if not text or len(text.strip()) < 100:
            return False, "Document is too short for meaningful analysis"
        
        # Check for signs of proper text extraction
        if len(text.split()) < 50:
            return False, "Document appears to have insufficient content"
        
        # Check for legal document indicators
        legal_indicators = ['agreement', 'contract', 'terms', 'conditions', 'party', 'clause', 'section']
        text_lower = text.lower()
        
        if not any(indicator in text_lower for indicator in legal_indicators):
            return False, "Document may not be a legal document or text extraction quality is poor"
        
        return True, "Document is suitable for analysis"