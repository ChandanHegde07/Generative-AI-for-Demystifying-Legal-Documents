def is_meaningful_content(text: str) -> bool:
    """Check if extracted content is meaningful."""
    if not text or text.strip() == "":
        return False
    text_lower = text.lower().strip()
    empty_patterns = [
        "**", "*", "not specified", "not mentioned", "not found",
        "not available", "no information", "details not provided",
        "information not available", "not listed", "not clearly mentioned"
    ]
    for pattern in empty_patterns:
        if text_lower == pattern or text_lower.startswith(pattern):
            return False
    meaningful_text = text_lower.replace("*", "").replace(" ", "").replace("-", "").replace("•", "")
    return len(meaningful_text) >= 15