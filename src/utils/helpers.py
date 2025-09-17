import re
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

def is_meaningful_content(text: str, min_words: int = 10) -> bool:
    if not text or not text.strip(): return False
    return len(text.split()) >= min_words

def extract_dates(text: str) -> List[str]:
    date_patterns = [
        r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}\b',
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{2,4}\b', r'\b\d{2,4}[-/]\d{1,2}[-/]\d{1,2}\b'
    ]
    dates = []
    for pattern in date_patterns: dates.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(set(dates))

def extract_amounts(text: str) -> List[str]:
    amount_patterns = [r'\$[\d,]+\.?\d*', r'USD\s*[\d,]+\.?\d*', r'INR\s*[\d,]+\.?\d*', r'Rs\.?\s*[\d,]+\.?\d*', r'₹\s*[\d,]+\.?\d*']
    amounts = []
    for pattern in amount_patterns: amounts.extend(re.findall(pattern, text, re.IGNORECASE))
    return amounts

def extract_emails(text: str) -> List[str]:
    return re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)

def extract_phone_numbers(text: str) -> List[str]:
    phone_patterns = [r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', r'\+?\d{1,3}[-.\s]?\d{10}', r'\(\d{3}\)\s*\d{3}-\d{4}']
    phones = []
    for pattern in phone_patterns: phones.extend(re.findall(pattern, text))
    return phones

def clean_text(text: str) -> str:
    if not text: return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\-.,;:()\'"$%@#!?/\\]', '', text)
    return text.strip()

def truncate_text(text: str, max_length: int = 1000) -> str:
    return text if len(text) <= max_length else text[:max_length] + "..."

def generate_text_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

def format_file_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024: return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def create_summary_stats(text: str) -> Dict[str, Any]:
    if not text: return {}
    words, sentences = text.split(), text.split('.')
    return {
        'character_count': len(text), 'word_count': len(words),
        'sentence_count': len([s for s in sentences if s.strip()]),
        'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
        'avg_words_per_sentence': len(words) / max(len(sentences), 1),
        'dates_found': len(extract_dates(text)), 'amounts_found': len(extract_amounts(text)),
        'emails_found': len(extract_emails(text)), 'phones_found': len(extract_phone_numbers(text))
    }

def validate_language(language: str, supported_languages: List[str]) -> bool:
    return language in supported_languages

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    return (timestamp or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")

def create_processing_log(filename: str, status: str, details: str = "") -> Dict[str, str]:
    return {'timestamp': format_timestamp(), 'filename': filename, 'status': status, 'details': details}

def extract_key_phrases(text: str, max_phrases: int = 20) -> List[str]:
    if not text: return []
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    important_keywords = ['agreement', 'contract', 'party', 'shall', 'must', 'required', 'liability', 'breach', 'termination', 'clause', 'section', 'payment', 'delivery', 'deadline', 'notice', 'rights']
    
    key_phrases = []
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in important_keywords):
            words = sentence.split()
            if 5 <= len(words) <= 15: key_phrases.append(sentence.strip())
    return list(set(key_phrases))[:max_phrases]

def create_document_dataframe(documents: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(documents) if documents else pd.DataFrame()

def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:200-len(ext)-1] + ('.' + ext if ext else '')
    return filename