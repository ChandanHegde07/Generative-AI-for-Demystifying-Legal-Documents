# src/utils/pii_anonymizer.py
import re
import hashlib
from typing import Dict, Tuple, List
import json

class PIIAnonymizer:
    """Anonymize Personally Identifiable Information in healthcare documents"""
    
    def __init__(self):
        self.pii_mapping: Dict[str, str] = {}
        self.reverse_mapping: Dict[str, str] = {}
        
    def _generate_placeholder(self, pii_type: str, value: str) -> str:
        """Generate a unique placeholder for a PII value"""
        # Create a short hash from the value for uniqueness
        hash_suffix = hashlib.md5(value.encode()).hexdigest()[:6].upper()
        placeholder = f"[{pii_type}_{hash_suffix}]"
        return placeholder
    
    def _detect_and_replace_emails(self, text: str) -> str:
        """Detect and replace email addresses"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        def replace_email(match):
            email = match.group(0)
            if email not in self.reverse_mapping:
                placeholder = self._generate_placeholder("EMAIL", email)
                self.pii_mapping[placeholder] = email
                self.reverse_mapping[email] = placeholder
            return self.reverse_mapping[email]
        
        return re.sub(email_pattern, replace_email, text)
    
    def _detect_and_replace_phones(self, text: str) -> str:
        """Detect and replace phone numbers (Indian and international formats)"""
        # Indian phone patterns: +91-9876543210, 9876543210, (91) 9876543210, etc.
        phone_patterns = [
            r'\+91[-\s]?\d{10}',  # +91-9876543210
            r'\(\+91\)[-\s]?\d{10}',  # (+91) 9876543210
            r'\b\d{10}\b',  # 9876543210
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 123-456-7890
        ]
        
        def replace_phone(match):
            phone = match.group(0)
            # Clean up the phone number
            cleaned = re.sub(r'[-\s\(\)]', '', phone)
            if len(cleaned) >= 10:  # Valid phone number
                if phone not in self.reverse_mapping:
                    placeholder = self._generate_placeholder("PHONE", phone)
                    self.pii_mapping[placeholder] = phone
                    self.reverse_mapping[phone] = placeholder
                return self.reverse_mapping[phone]
            return phone
        
        for pattern in phone_patterns:
            text = re.sub(pattern, replace_phone, text)
        return text
    
    def _detect_and_replace_aadhaar(self, text: str) -> str:
        """Detect and replace Aadhaar numbers (12-digit Indian ID)"""
        # Aadhaar: 1234 5678 9012 or 123456789012
        aadhaar_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        
        def replace_aadhaar(match):
            aadhaar = match.group(0)
            cleaned = re.sub(r'[\s-]', '', aadhaar)
            if len(cleaned) == 12:  # Valid Aadhaar
                if aadhaar not in self.reverse_mapping:
                    placeholder = self._generate_placeholder("ID", aadhaar)
                    self.pii_mapping[placeholder] = aadhaar
                    self.reverse_mapping[aadhaar] = placeholder
                return self.reverse_mapping[aadhaar]
            return aadhaar
        
        return re.sub(aadhaar_pattern, replace_aadhaar, text)
    
    def _detect_and_replace_dates(self, text: str) -> str:
        """Detect and replace dates"""
        # Common date formats: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, Month DD, YYYY
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # DD/MM/YYYY, DD-MM-YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',  # YYYY-MM-DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
        ]
        
        def replace_date(match):
            date = match.group(0)
            if date not in self.reverse_mapping:
                placeholder = self._generate_placeholder("DATE", date)
                self.pii_mapping[placeholder] = date
                self.reverse_mapping[date] = placeholder
            return self.reverse_mapping[date]
        
        for pattern in date_patterns:
            text = re.sub(pattern, replace_date, text, flags=re.IGNORECASE)
        return text
    
    def _detect_and_replace_names(self, text: str) -> str:
        """Detect and replace person names using common patterns"""
        # This is a simple heuristic - for better results, use NER (Named Entity Recognition)
        # Pattern: Capitalized words that might be names
        # Common Indian name patterns
        name_patterns = [
            r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Title + Name
            r'\bPatient:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Patient: Name
            r'\bDoctor:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Doctor: Name
            r'\bName:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Name: ...
        ]
        
        def replace_name(match):
            name = match.group(1) if match.lastindex else match.group(0)
            # Remove titles
            name = re.sub(r'^(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+', '', name)
            
            if len(name.split()) >= 1 and len(name) > 2:  # Valid name
                if name not in self.reverse_mapping:
                    placeholder = self._generate_placeholder("PERSON", name)
                    self.pii_mapping[placeholder] = name
                    self.reverse_mapping[name] = placeholder
                return match.group(0).replace(name, self.reverse_mapping[name])
            return match.group(0)
        
        for pattern in name_patterns:
            text = re.sub(pattern, replace_name, text)
        return text
    
    def _detect_and_replace_organizations(self, text: str) -> str:
        """Detect and replace organization names"""
        org_patterns = [
            r'\b(?:Hospital|Clinic|Medical Center|Healthcare|Diagnostics):\s*([A-Z][A-Za-z\s&]+)(?=\n|,|\.)',
            r'\b([A-Z][A-Za-z\s&]+(?:Hospital|Clinic|Medical Center|Healthcare|Diagnostics))\b',
        ]
        
        def replace_org(match):
            org = match.group(1) if match.lastindex else match.group(0)
            org = org.strip()
            
            if len(org) > 3:  # Valid organization name
                if org not in self.reverse_mapping:
                    placeholder = self._generate_placeholder("ORG", org)
                    self.pii_mapping[placeholder] = org
                    self.reverse_mapping[org] = placeholder
                return match.group(0).replace(org, self.reverse_mapping[org])
            return match.group(0)
        
        for pattern in org_patterns:
            text = re.sub(pattern, replace_org, text)
        return text
    
    def _detect_and_replace_locations(self, text: str) -> str:
        """Detect and replace location/address information"""
        location_patterns = [
            r'\b\d+[A-Za-z]?\s+[A-Z][A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr)\b',  # Street addresses
            r'\b(?:Address|Location):\s*([A-Z][A-Za-z0-9\s,.-]+)(?=\n|Patient|Doctor)',
        ]
        
        def replace_location(match):
            location = match.group(1) if match.lastindex else match.group(0)
            location = location.strip()
            
            if len(location) > 5:  # Valid location
                if location not in self.reverse_mapping:
                    placeholder = self._generate_placeholder("GPE", location)
                    self.pii_mapping[placeholder] = location
                    self.reverse_mapping[location] = placeholder
                return match.group(0).replace(location, self.reverse_mapping[location])
            return match.group(0)
        
        for pattern in location_patterns:
            text = re.sub(pattern, replace_location, text)
        return text
    
    def anonymize(self, text: str, reset_mappings: bool = False) -> Tuple[str, Dict[str, str]]:
        """
        Anonymize all PII in the text and return anonymized text + mapping
        
        Args:
            text: Original text with PII
            reset_mappings: If True, clear existing mappings before processing (default: False)
            
        Returns:
            Tuple of (anonymized_text, pii_mapping)
        """
        # Only reset mappings if explicitly requested (for new document)
        if reset_mappings:
            self.pii_mapping = {}
            self.reverse_mapping = {}
        
        # Apply all detection and replacement methods in order
        text = self._detect_and_replace_emails(text)
        text = self._detect_and_replace_phones(text)
        text = self._detect_and_replace_aadhaar(text)
        text = self._detect_and_replace_dates(text)
        text = self._detect_and_replace_names(text)
        text = self._detect_and_replace_organizations(text)
        text = self._detect_and_replace_locations(text)
        
        return text, self.pii_mapping
    
    def deanonymize(self, text: str, pii_mapping: Dict[str, str]) -> str:
        """
        Restore original PII from anonymized text
        
        Args:
            text: Anonymized text
            pii_mapping: Mapping from placeholders to original values
            
        Returns:
            Original text with PII restored
        """
        for placeholder, original_value in pii_mapping.items():
            text = text.replace(placeholder, original_value)
        return text
    
    def get_pii_summary(self) -> str:
        """Get a formatted summary of detected PII"""
        if not self.pii_mapping:
            return "No PII detected."
        
        summary = "🗺️ PII Mapping:\n{\n"
        for placeholder, value in sorted(self.pii_mapping.items()):
            summary += f'    "{placeholder}": "{value}",\n'
        summary = summary.rstrip(',\n') + '\n}'
        
        return summary
    
    def export_mapping(self) -> str:
        """Export PII mapping as JSON string"""
        return json.dumps(self.pii_mapping, indent=2)
    
    def import_mapping(self, json_str: str):
        """Import PII mapping from JSON string"""
        self.pii_mapping = json.loads(json_str)
        self.reverse_mapping = {v: k for k, v in self.pii_mapping.items()}
