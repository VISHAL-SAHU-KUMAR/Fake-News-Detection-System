def extract_and_clean_claim(raw_text: str) -> str:
    """
    Cleans up the text by removing 'forwarded many times', extra spaces, etc.
    """
    clean_text = raw_text.strip()
    
    # Remove common WhatsApp prefixes
    common_prefixes = [
        "Forwarded many times",
        "Forwarded",
        "WhatsApp Forward:",
        "As received:"
    ]
    
    for prefix in common_prefixes:
        # Check case-insensitive start
        if clean_text.lower().startswith(prefix.lower()):
            clean_text = clean_text[len(prefix):].strip()
            
    # Remove large chunks of whitespace
    clean_text = " ".join(clean_text.split())
    
    return clean_text
