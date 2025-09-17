# src/utils/helpers.py - Helper utility functions
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

def is_meaningful_content(text: str, min_words: int = 10) -> bool:
    """Check if text contains meaningful content"""
    if not text or not text.strip():
        return False
    
    words = text.split()
    return len(words) >= min_words

def extract_dates(text: str) -> List[str]:
    """Extract potential dates from text using regex"""
    date_patterns = [
        r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',  # MM/DD/YYYY or MM-DD-YYYY
        r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}\b',
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{2,4}\b',
        r'\b\d{2,4}[-/]\d{1,2}[-/]\d{1,2}\b'  # YYYY/MM/DD
    ]
    
    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(matches)
    
    return list(set(dates))  # Remove duplicates

def extract_amounts(text: str) -> List[str]:
    """Extract monetary amounts from text"""
    amount_patterns = [
        r'\$[\d,]+\.?\d*',  # $1,000.00
        r'USD\s*[\d,]+\.?\d*',  # USD 1000
        r'INR\s*[\d,]+\.?\d*',  # INR 1000
        r'Rs\.?\s*[\d,]+\.?\d*',  # Rs. 1000
        r'₹\s*[\d,]+\.?\d*'  # ₹1000
    ]
    
    amounts = []
    for pattern in amount_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        amounts.extend(matches)
    
    return amounts

def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text"""
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
        r'\+?\d{1,3}[-.\s]?\d{10}',  # 10 digit numbers
        r'\(\d{3}\)\s*\d{3}-\d{4}'  # (123) 456-7890
    ]
    
    phones = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phones.extend(matches)
    
    return phones

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might interfere with processing
    text = re.sub(r'[^\w\s\-.,;:()\'"$%@#!?/\\]', '', text)
    
    return text.strip()

def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."

def generate_text_hash(text: str) -> str:
    """Generate a hash for text content"""
    return hashlib.md5(text.encode()).hexdigest()

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def create_summary_stats(text: str) -> Dict[str, Any]:
    """Create summary statistics for text"""
    if not text:
        return {}
    
    words = text.split()
    sentences = text.split('.')
    
    return {
        'character_count': len(text),
        'word_count': len(words),
        'sentence_count': len([s for s in sentences if s.strip()]),
        'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
        'avg_words_per_sentence': len(words) / max(len(sentences), 1),
        'dates_found': len(extract_dates(text)),
        'amounts_found': len(extract_amounts(text)),
        'emails_found': len(extract_emails(text)),
        'phones_found': len(extract_phone_numbers(text))
    }

def validate_language(language: str, supported_languages: List[str]) -> bool:
    """Validate if language is supported"""
    return language in supported_languages

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """Format timestamp for logging"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def create_processing_log(filename: str, status: str, details: str = "") -> Dict[str, str]:
    """Create a processing log entry"""
    return {
        'timestamp': format_timestamp(),
        'filename': filename,
        'status': status,
        'details': details
    }

def extract_key_phrases(text: str, max_phrases: int = 20) -> List[str]:
    """Extract potential key phrases from text using simple heuristics"""
    if not text:
        return []
    
    # Split into sentences
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    key_phrases = []
    
    # Look for phrases that might be important (capitalized, contain certain keywords)
    important_keywords = [
        'agreement', 'contract', 'party', 'shall', 'must', 'required',
        'liability', 'breach', 'termination', 'clause', 'section',
        'payment', 'delivery', 'deadline', 'notice', 'rights'
    ]
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        
        # Check if sentence contains important keywords
        if any(keyword in sentence_lower for keyword in important_keywords):
            # Extract phrases (simple approach - could be improved)
            words = sentence.split()
            if 5 <= len(words) <= 15:  # Reasonable phrase length
                key_phrases.append(sentence.strip())
    
    # Return unique phrases, limited to max_phrases
    return list(set(key_phrases))[:max_phrases]

def create_document_dataframe(documents: List[Dict[str, Any]]) -> pd.DataFrame:
    """Create a pandas DataFrame from document processing results"""
    if not documents:
        return pd.DataFrame()
    
    return pd.DataFrame(documents)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:200-len(ext)-1] + ('.' + ext if ext else '')
    
    return filename