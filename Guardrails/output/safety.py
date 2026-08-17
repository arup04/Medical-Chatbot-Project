# Guardrails/output/safety.py
import re
from typing import List, Pattern, Tuple
from .models import OutputGuardrailResult

OUTPUT_SAFETY_BLOCKED_MESSAGE = (
    "⚠️ **OUTPUT SAFETY INTERCEPTION**\n\n"
    "The generated response contained prescriptive dosage instructions or potentially unsafe self-treatment advice and was blocked for your safety.\n\n"
    "Please consult a licensed medical doctor or certified healthcare provider for individualized diagnosis, treatment, and medication prescriptions."
)

# Patterns that MUST NOT appear in LLM generated responses
HARMFUL_OUTPUT_PATTERNS_RAW: List[Tuple[str, str]] = [
    # Prescriptive dosage directives (e.g., "take 500 mg 3 times a day", "take 2 tablets")
    (
        r"\b(?:you should take|take|prescribed dose is|ingest|administer)\s+\d+\s*(?:mg|milligrams?|g|grams?|tablets?|pills?|capsules?|drops?)\b.*(?:daily|every\s+\d+|times?\s+a\s+day|before bedtime|per day)",
        "prescriptive_dosage_directive"
    ),
    (
        r"\b(?:take|consume)\s+\d+\s+(?:tablets?|pills?|capsules?)\s+(?:daily|every|each day|a day)\b",
        "prescriptive_tablet_quantity"
    ),

    # Dangerous DIY surgical / invasive procedures at home
    (
        r"\b(?:cut|lance|drain|incise|puncture)\s+(?:the\s+)?(?:boil|abscess|cyst|wound|skin)\s+(?:yourself|at home|with a (?:needle|blade|knife|razor|scissors))\b",
        "diy_invasive_procedure"
    ),
    (
        r"\bperform (?:surgery|an incision|minor surgery) (?:at home|yourself)\b",
        "diy_surgery"
    ),

    # Toxic / harmful pseudo-medical advice
    (
        r"\b(?:drink|ingest|consume)\s+(?:bleach|hydrogen peroxide|colloidal silver|kerosene|borax|detergent)\b",
        "toxic_ingestion_advice"
    ),
    (
        r"\b(?:stop|discontinue|abandon)\s+(?:taking\s+)?(?:chemotherapy|insulin|antiretroviral|dialysis|heart medication)\b.*(?:replace with|instead of|natural cures?)",
        "dangerous_treatment_discontinuation"
    ),
]

COMPILED_OUTPUT_PATTERNS: List[Tuple[Pattern, str]] = [
    (re.compile(pat, re.IGNORECASE), violation_tag)
    for pat, violation_tag in HARMFUL_OUTPUT_PATTERNS_RAW
]


def check_output_safety(response_text: str) -> OutputGuardrailResult:
    """
    Scans the LLM-generated response for prescriptive dosage instructions,
    dangerous DIY procedures, or harmful toxic advice.
    """
    if not response_text or not response_text.strip():
        return OutputGuardrailResult(
            passed=True,
            guardrail="safety",
            action="pass",
            output_text=response_text,
        )

    violations = []
    for pattern, tag in COMPILED_OUTPUT_PATTERNS:
        match = pattern.search(response_text)
        if match:
            violations.append(f"{tag}: '{match.group(0)}'")

    if violations:
        return OutputGuardrailResult(
            passed=False,
            guardrail="safety",
            action="block",
            reason=f"Harmful or prescriptive output detected ({', '.join(violations)})",
            violations=violations,
            output_text=OUTPUT_SAFETY_BLOCKED_MESSAGE,
        )

    return OutputGuardrailResult(
        passed=True,
        guardrail="safety",
        action="pass",
        output_text=response_text,
    )
