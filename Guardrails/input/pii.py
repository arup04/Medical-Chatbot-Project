# Guardrails/input/pii.py
import re
from typing import Tuple, List
from .models import GuardrailResult

# PII pattern definitions
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
)

PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    r"|\b(?:\+91[-.\s]?)?[6-9]\d{9}\b"
)

SSN_PATTERN = re.compile(
    r"\b\d{3}-\d{2}-\d{4}\b"
)

AADHAAR_PATTERN = re.compile(
    r"\b\d{4}\s\d{4}\s\d{4}\b"
)

# Context-aware patient name introduction patterns
NAME_INTRO_PATTERNS = [
    (re.compile(r"\b(?:my name is|i am|i'm)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", re.IGNORECASE), "My name is <PATIENT_NAME>"),
    (re.compile(r"\b(?:patient name(?:\s+is)?|patient:)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", re.IGNORECASE), "Patient: <PATIENT_NAME>"),
]


def sanitize_pii_text(text: str) -> Tuple[str, List[str]]:
    """
    Sanitizes personally identifiable information (PII / PHI) from text.
    
    Returns:
        Tuple of (sanitized_string, list_of_detected_pii_types)
    """
    detected = []
    sanitized = text

    # 1. Email Redaction
    if EMAIL_PATTERN.search(sanitized):
        sanitized = EMAIL_PATTERN.sub("<EMAIL_REDACTED>", sanitized)
        detected.append("email")

    # 2. SSN Redaction
    if SSN_PATTERN.search(sanitized):
        sanitized = SSN_PATTERN.sub("<SSN_REDACTED>", sanitized)
        detected.append("ssn")

    # 3. Aadhaar Redaction
    if AADHAAR_PATTERN.search(sanitized):
        sanitized = AADHAAR_PATTERN.sub("<AADHAAR_REDACTED>", sanitized)
        detected.append("aadhaar")

    # 4. Phone Number Redaction
    if PHONE_PATTERN.search(sanitized):
        sanitized = PHONE_PATTERN.sub("<PHONE_REDACTED>", sanitized)
        detected.append("phone_number")

    # 5. Patient Name Introduction Redaction
    for pat, repl in NAME_INTRO_PATTERNS:
        if pat.search(sanitized):
            sanitized = pat.sub(repl, sanitized)
            detected.append("patient_name")

    return sanitized, detected


def check_and_sanitize_pii(user_input: str) -> GuardrailResult:
    """
    Inspects user input for PII/PHI. If found, sanitizes the query and returns
    action='sanitize' with the redacted query in sanitized_input.
    If no PII is found, returns action='pass'.
    """
    if not user_input or not user_input.strip():
        return GuardrailResult(
            triggered=False,
            guardrail="pii",
            action="pass",
            sanitized_input=user_input,
        )

    sanitized_text, detected_types = sanitize_pii_text(user_input)

    if detected_types:
        return GuardrailResult(
            triggered=True,
            guardrail="pii",
            action="sanitize",
            reason=f"PII/PHI detected and sanitized: {', '.join(set(detected_types))}",
            sanitized_input=sanitized_text,
        )

    return GuardrailResult(
        triggered=False,
        guardrail="pii",
        action="pass",
        sanitized_input=user_input,
    )
