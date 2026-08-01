import re
from typing import Dict

def sniff_contact(cv_text: str) -> Dict[str, str]:
    """
    Extract best-effort contact details (Name, Email, Phone, Location) from CV text.
    """
    details = {
        "name": "Candidate",
        "email": "",
        "phone": "",
        "location": ""
    }

    if not cv_text:
        return details

    # Extract Email
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", cv_text)
    if email_match:
        details["email"] = email_match.group(0)

    # Extract Phone
    phone_match = re.search(r"\(?\+?\d{1,3}\)?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", cv_text)
    if phone_match:
        details["phone"] = phone_match.group(0)

    # Extract Name (Heuristic: usually first non-empty line of CV)
    lines = [ln.strip() for ln in cv_text.splitlines() if ln.strip()]
    if lines:
        first_line = lines[0]
        # Ignore titles or section headers
        if len(first_line) < 40 and not any(kw in first_line.lower() for kw in ["resume", "curriculum", "cv", "experience", "profile"]):
            # Strip non-alphanumeric trailing/leading characters
            clean_name = re.sub(r"[^\w\s-]", "", first_line).strip()
            if clean_name:
                details["name"] = clean_name

    # Extract Location (City, State / Country heuristic)
    loc_match = re.search(r"([A-Z][a-zA-Z\s]+,\s*(?:[A-Z]{2}|[A-Z][a-zA-Z\s]+))", cv_text)
    if loc_match:
        loc = loc_match.group(1).strip()
        if len(loc) < 50:
            details["location"] = loc

    return details
