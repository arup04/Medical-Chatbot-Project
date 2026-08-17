# Guardrails/input/dosage.py
import re
from typing import List, Pattern
from .models import GuardrailResult

DOSAGE_BLOCKED_MESSAGE = (
    "💊 **PRESCRIPTION & DOSAGE INQUIRY RESTRICTION**\n\n"
    "MediAid AI is strictly an educational reference tool and **cannot provide prescriptive medication dosages, tablet quantities, or personalized treatment regimens.**\n\n"
    "Medication dosages must be individualized based on your age, body weight, kidney/liver function, underlying conditions, and possible drug interactions.\n\n"
    "**Please consult a licensed physician or pharmacist** to determine the safe, appropriate dosage and prescription for your condition."
)

DOSAGE_PATTERNS_RAW: List[str] = [
    # Explicit inquiries about dosage/dose of drugs, tablets, medications
    r"\b(?:what is|what are|tell me|give me)\b.*(?:dosage|dose)\b",
    r"\b(?:dosage|dose)\b.*(?:of|for)?.*(?:tablets?|pills?|capsules?|medications?|medicines?|drugs?)\b",
    r"\b(?:tablets?|pills?|capsules?|medications?|medicines?|drugs?)\b.*(?:dosage|dose)\b",
    r"\b(?:drug|medication|tablet|pill)\s+(?:dosage|dose)\b",
    
    # "how many / how much" tablets, pills, mg, dosage
    r"\bhow (?:much|many)\b.*(?:tablets?|pills?|capsules?|drops?|doses?|dosage|mg|milligrams?|grams?|ml)\b",
    
    # "how often / frequency to take"
    r"\bhow (?:often|frequently|many times a day)\b.*(?:take|consume|use|ingest)\b",
    
    # Recommended / safe / maximum / standard dosage modifiers
    r"\b(?:safe|recommended|maximum|standard|correct|proper|appropriate|daily|starting|lethal)\s+(?:dosage|dose)\b",
    
    # "can I take [X] mg / tablets"
    r"\b(?:can|should|could|may) I (?:take|consume|use|have|increase|double|reduce|lower)\b.*\d+\s*(?:mg|milligrams?|g|grams?|tablets?|pills?|capsules?|ml|drops?)",
    r"\b(?:can|should|could|may) I (?:take|consume|use)\b.*(?:tablets?|pills?|capsules?|dose|dosage)",
    
    # Prescriptions and administration charts
    r"\b(?:prescribe|write a prescription for|give me a prescription for|need a prescription)\b",
    r"\b(?:tablet|pill|medication|drug) (?:schedule|regimen|dosage chart)\b",
]

COMPILED_DOSAGE_PATTERNS: List[Pattern] = [
    re.compile(pat, re.IGNORECASE) for pat in DOSAGE_PATTERNS_RAW
]


def check_dosage(user_input: str) -> GuardrailResult:
    """
    Inspects user input to detect requests for drug dosages, tablet quantities,
    prescriptions, or personal medication administration instructions.
    
    Returns:
        GuardrailResult with action='block' and dosage warning message if triggered,
        otherwise action='pass'.
    """
    if not user_input or not user_input.strip():
        return GuardrailResult(
            triggered=False,
            guardrail="dosage",
            action="pass",
        )

    normalized_input = user_input.strip()

    for pattern in COMPILED_DOSAGE_PATTERNS:
        match = pattern.search(normalized_input)
        if match:
            matched_phrase = match.group(0)
            return GuardrailResult(
                triggered=True,
                guardrail="dosage",
                action="block",
                reason=f"Medication dosage or prescription inquiry detected: '{matched_phrase}'",
                message=DOSAGE_BLOCKED_MESSAGE,
            )

    return GuardrailResult(
        triggered=False,
        guardrail="dosage",
        action="pass",
    )
