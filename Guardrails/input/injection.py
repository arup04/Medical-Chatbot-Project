# Guardrails/input/injection.py
import re
from typing import List, Pattern
from .models import GuardrailResult

INJECTION_BLOCKED_MESSAGE = (
    "🛡️ **SECURITY RESTRICTION: PROMPT INJECTION / JAILBREAK DETECTED**\n\n"
    "Your request contains system instruction overrides, jailbreak patterns, or disallowed commands.\n\n"
    "MediAid AI is strictly configured to answer clinical and educational health questions based on medical literature. "
    "Please rephrase your inquiry to focus on valid medical knowledge."
)

INJECTION_PATTERNS_RAW: List[str] = [
    # System instruction bypass & prompt extraction
    r"\b(?:ignore|disregard|override|forget|bypass)\s+(?:all\s+)?(?:previous|prior|system|initial|above)\s+(?:instructions|guidelines|rules|prompts?)\b",
    r"\b(?:show|print|reveal|display|output|tell|give)\s+(?:me\s+|us\s+)?(?:your\s+)?(?:system prompt|initial instructions|hidden prompt|developer prompt|developer instructions|system instructions)\b",
    r"\b(?:what is|what are|what were)\s+(?:your\s+)?(?:system prompt|initial instructions|developer instructions|system instructions)\b",
    r"\brepeat (?:the words |everything )?(?:above|before this)\b",

    # Roleplay & Jailbreaks (DAN, Developer Mode, Persona hacks)
    r"\b(?:you are now in|switch to|enter)\s+(?:dan|developer|god|unrestricted|jailbreak|maintenance)\s+mode\b",
    r"\bdo anything now\b",
    r"\bpretend (?:to be|you are)\s+(?:an evil|an unrestricted|a malicious|a rogue|a criminal)\b",
    r"\bignore safety (?:filters|protocols|guidelines|policies)\b",
    r"\bfor educational purposes only, (?:bypass|ignore|generate disallowed)\b",

    # Harmful / Illicit weaponized or chemical queries
    r"\bhow to (?:synthesize|manufacture|cook|produce|brew)\s+(?:methamphetamine|meth|cocaine|heroin|fentanyl|illegal drugs?|poison|explosives?|mustard gas)\b",
    r"\bhow to (?:extract|weaponize)\s+(?:ricin|anthrax|cyanide|botulinum|toxins?)\b",

    # Prompt structure injection tokens
    r"(?:\[SYSTEM\]|\[INST\]|<<SYS>>|<\|im_start\|>system|<\|system\|>)",
]

COMPILED_INJECTION_PATTERNS: List[Pattern] = [
    re.compile(pat, re.IGNORECASE) for pat in INJECTION_PATTERNS_RAW
]


def check_injection(user_input: str) -> GuardrailResult:
    """
    Inspects user input for prompt injection attempts, jailbreaks, system prompt
    extraction, or illicit chemical/toxic synthesis commands.
    
    Returns:
        GuardrailResult with action='block' if injection detected, otherwise action='pass'.
    """
    if not user_input or not user_input.strip():
        return GuardrailResult(
            triggered=False,
            guardrail="injection",
            action="pass",
        )

    normalized_input = user_input.strip()

    for pattern in COMPILED_INJECTION_PATTERNS:
        match = pattern.search(normalized_input)
        if match:
            matched_phrase = match.group(0)
            return GuardrailResult(
                triggered=True,
                guardrail="injection",
                action="block",
                reason=f"Prompt injection or jailbreak attempt detected: '{matched_phrase}'",
                message=INJECTION_BLOCKED_MESSAGE,
            )

    return GuardrailResult(
        triggered=False,
        guardrail="injection",
        action="pass",
    )
