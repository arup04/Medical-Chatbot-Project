# Guardrails/input/emergency.py
import re
from typing import Dict, List, Pattern
from .models import GuardrailResult

EMERGENCY_RESPONSE_MESSAGE = (
    "🚨 **CRITICAL MEDICAL EMERGENCY DETECTED**\n\n"
    "If you or someone near you is experiencing severe symptoms or a medical emergency, "
    "**please visit a doctor or go to the nearest hospital / emergency room immediately.**\n\n"
    "⚠️ *MediAid AI is an educational reference tool and cannot provide emergency medical care or evaluate life-threatening conditions.*"
)

# Comprehensive category patterns for acute emergencies
EMERGENCY_PATTERNS_RAW: Dict[str, List[str]] = {
    "acute_breathing_distress": [
        r"\bcan'?t breathe\b",
        r"\bcannot breathe\b",
        r"\bcan'?t catch (?:my|their|his|her) breath\b",
        r"\bsevere (?:shortness of breath|difficulty breathing|breathlessness)\b",
        r"\bgasping for (?:air|breath)\b",
        r"\bchoking and (?:can'?t|cannot) breathe\b",
        r"\bsuffocating\b",
    ],
    "severe_cardiac_symptoms": [
        r"\b(?:crushing|severe|intense|radiating) chest pain\b",
        r"\bchest pain.*(?:radiating to|left arm|jaw|neck|back)\b",
        r"\b(?:having a|think I'?m having a|suspect a) heart attack\b",
        r"\bheavy pressure on (?:my|the) chest.*(?:dizzy|sweating|sweat|short of breath)\b",
    ],
    "unconsciousness_and_collapse": [
        r"\bunconscious and not (?:responding|waking up|breathing)\b",
        r"\bpassed out and (?:won'?t|cannot|can'?t) wake up\b",
        r"\bperson (?:is|became) unresponsive\b",
        r"\bfound (?:someone|him|her) collapsed and not responding\b",
    ],
    "severe_uncontrolled_bleeding": [
        r"\b(?:severe|uncontrolled|massive|arterial) bleeding\b",
        r"\bbleeding (?:won'?t|will not|doesn'?t|does not) stop\b",
        r"\bgushing blood\b",
        r"\bcoughed up large amounts of blood\b",
        r"\bvomi(?:t|ting) (?:large amounts of |fresh )?blood\b",
    ],
    "acute_stroke_indicators": [
        r"\bsudden (?:numbness|weakness|paralysis) on one side\b",
        r"\b(?:face|mouth) (?:is )?drooping.*(?:arm|speech)\b",
        r"\bsudden (?:loss of speech|slurred speech|inability to speak)\b",
        r"\bsudden loss of vision.*slurred speech\b",
    ],
    "anaphylaxis_and_airway_closure": [
        r"\bthroat (?:is closing|swelling shut|closing up)\b",
        r"\bsevere allergic reaction.*(?:can'?t breathe|throat)\b",
        r"\banaphylactic shock\b",
        r"\btongue is (?:severely )?swollen and (?:can'?t|cannot) breathe\b",
    ],
    "acute_poisoning_or_overdose": [
        r"\b(?:swallowed|drank|ingested) (?:poison|bleach|detergent|toxic chemicals?|battery)\b",
        r"\b(?:drug|medication|pill) overdose\b",
        r"\boverdosed on\b",
        r"\btook (?:a whole|entire|too many) (?:bottle|pack|strip|handful) of (?:pills|tablets|medication)\b",
    ],
    "acute_crisis_and_self_harm": [
        r"\b(?:want to|going to|plan to) (?:kill myself|commit suicide|end my life)\b",
        r"\bhow to (?:commit suicide|kill myself)\b",
        r"\b(?:suicide|suicidal) plan\b",
    ],
}

# Compile patterns once for high-throughput performance
COMPILED_PATTERNS: Dict[str, List[Pattern]] = {
    category: [re.compile(pat, re.IGNORECASE) for pat in patterns]
    for category, patterns in EMERGENCY_PATTERNS_RAW.items()
}


def check_emergency(user_input: str) -> GuardrailResult:
    """
    Inspects user input for indicators of acute medical emergencies or life-threatening crises.
    
    Returns:
        GuardrailResult with action='block' and an emergency message if triggered,
        otherwise action='pass'.
    """
    if not user_input or not user_input.strip():
        return GuardrailResult(
            triggered=False,
            guardrail="emergency",
            action="pass",
        )

    normalized_input = user_input.strip()

    for category, patterns in COMPILED_PATTERNS.items():
        for pattern in patterns:
            match = pattern.search(normalized_input)
            if match:
                matched_phrase = match.group(0)
                return GuardrailResult(
                    triggered=True,
                    guardrail="emergency",
                    action="block",
                    reason=f"Acute emergency condition detected ({category}: '{matched_phrase}')",
                    message=EMERGENCY_RESPONSE_MESSAGE,
                )

    return GuardrailResult(
        triggered=False,
        guardrail="emergency",
        action="pass",
    )
