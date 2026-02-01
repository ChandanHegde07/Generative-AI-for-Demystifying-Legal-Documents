"""
Script to update document_parser.py with PII anonymization methods
Run this from the project root: python update_parser.py
"""

import os

file_path = 'src/utils/document_parser.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_method = '''    def extract_text_from_file(self, uploaded_file: Any) -> str:
        """Extract text from a single uploaded file"""
        if uploaded_file.type == "application/pdf":
            return self._extract_text_pdf(uploaded_file)
        elif uploaded_file.type.startswith('image/'):
            return self._extract_text_image(uploaded_file)
        elif uploaded_file.type == "text/plain":
            return uploaded_file.getvalue().decode('utf-8')
        raise ValueError(f"Unsupported file type: {uploaded_file.type}")'''

new_methods = '''    def extract_text_from_file(self, uploaded_file: Any) -> str:
        """Extract text from a single uploaded file"""
        if uploaded_file.type == "application/pdf":
            text = self._extract_text_pdf(uploaded_file)
        elif uploaded_file.type.startswith('image/'):
            text = self._extract_text_image(uploaded_file)
        elif uploaded_file.type == "text/plain":
            text = uploaded_file.getvalue().decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {uploaded_file.type}")
        
        # Apply PII anonymization if enabled
        if self.enable_pii_anonymization and self.anonymizer and text:
            anonymized_text, pii_mapping = self.anonymizer.anonymize(text)
            self.pii_mapping.update(pii_mapping)
            return anonymized_text
        
        return text
    
    def get_pii_mapping(self) -> Dict[str, str]:
        """Get the PII mapping for extracted documents"""
        return self.pii_mapping
    
    def get_pii_summary(self) -> str:
        """Get a formatted summary of detected PII"""
        if self.anonymizer:
            return self.anonymizer.get_pii_summary()
        return "PII anonymization is disabled."
    
    def deanonymize_text(self, text: str) -> str:
        """Restore original PII in text"""
        if self.anonymizer and self.pii_mapping:
            return self.anonymizer.deanonymize(text, self.pii_mapping)
        return text'''

if old_method in content:
    content = content.replace(old_method, new_methods)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Successfully updated document_parser.py with PII anonymization methods!")
    print("\nAdded methods:")
    print("  - extract_text_from_file (updated)")
    print("  - get_pii_mapping()")
    print("  - get_pii_summary()")
    print("  - deanonymize_text()")
else:
    print("Could not find the method to replace. File may already be updated.")
    print("\nPlease check if the file has been modified manually.")
