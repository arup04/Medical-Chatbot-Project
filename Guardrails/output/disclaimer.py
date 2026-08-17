# Guardrails/output/disclaimer.py
from .models import OutputGuardrailResult

MANDATORY_DISCLAIMER = (
    "\n\n---\n*⚠️ **Disclaimer**: MediAid AI is an educational reference tool grounded in medical literature. "
    "It does not provide formal clinical diagnoses, personalized treatment plans, or prescriptions. "
    "Always consult a licensed physician or healthcare professional for any medical concerns.*"
)

# Standard refusal phrases that do not require an educational disclaimer
REFUSAL_PHRASES = [
    "i don't have information on that topic",
    "i do not have information on that topic",
    "critical medical emergency detected",
    "prescription & dosage inquiry restriction",
    "prompt injection / jailbreak detected",
]


def should_append_disclaimer(text: str) -> bool:
    """
    Determines whether a clinical response requires a mandatory disclaimer.
    Simple refusals or security blocks do not require redundant disclaimers.
    """
    if not text or not text.strip():
        return False

    normalized = text.lower()

    # If disclaimer is already present, don't duplicate
    if "disclaimer" in normalized and "mediaid" in normalized:
        return False

    # Check if text is a simple refusal or guardrail block
    for phrase in REFUSAL_PHRASES:
        if phrase in normalized:
            return False

    return True


def apply_disclaimer(response_text: str) -> OutputGuardrailResult:
    """
    Appends the mandatory clinical disclaimer to AI-generated medical answers.
    """
    if not should_append_disclaimer(response_text):
        return OutputGuardrailResult(
            passed=True,
            guardrail="disclaimer",
            action="pass",
            output_text=response_text,
        )

    modified_text = response_text.rstrip() + MANDATORY_DISCLAIMER
    return OutputGuardrailResult(
        passed=True,
        guardrail="disclaimer",
        action="modify",
        reason="Appended mandatory clinical and regulatory disclaimer footer.",
        output_text=modified_text,
    )
