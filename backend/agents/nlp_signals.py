import re

EMOTIVE_WORDS = [
    "shocking", "urgent", "must read", "secret", "exposed", "scam",
    "banned", "deleted", "conspiracy", "hoax", "miracle", "cure", "forward to everyone",
    "omg", "warning", "breaking", "viral", "attention"
]

def analyze_nlp_signals(text: str) -> list[str]:
    flags = []
    text_lower = text.lower()
    
    # Check for excessive capitalization
    words = text.split()
    caps_count = sum(1 for w in words if w.isupper() and len(w) > 1)
    if caps_count > 2 or (len(words) > 0 and caps_count / len(words) > 0.3):
        flags.append("Excessive use of ALL CAPS")
        
    # Check for excessive exclamation marks
    if "!!!" in text or text.count("!") > 2:
        flags.append("Excessive use of exclamation marks")
        
    # Check for emotive language
    found_emotive = [word for word in EMOTIVE_WORDS if word in text_lower]
    if found_emotive:
        flags.append(f"Contains sensational or emotive language ({', '.join(found_emotive)})")
        
    # Check for forward instructions (WhatsApp specific)
    if any(phrase in text_lower for phrase in ["forward this", "share this", "send this to", "broadcast this"]):
        flags.append("Contains chain message instructions typical of spam/hoaxes")
        
    return flags
