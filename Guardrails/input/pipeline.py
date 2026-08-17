# Guardrails/input/pipeline.py
from typing import Tuple
from .models import GuardrailResult
from .emergency import check_emergency
from .dosage import check_dosage
from .injection import check_injection
from .pii import check_and_sanitize_pii


def run_input_guardrails(user_input: str) -> GuardrailResult:
    """
    Orchestrates all Input Guardrails in priority sequence:
    
    1. 🚨 Emergency Triage: Checks for acute life-threatening emergencies. (DETECT -> BLOCK)
    2. 💊 Dosage Blocker: Checks for prescription / tablet dosage inquiries. (DETECT -> BLOCK)
    3. 🛡️ Prompt Injection: Checks for jailbreaks, prompt extraction, or chemical weapons. (DETECT -> BLOCK)
    4. 🔒 PII/PHI Sanitizer: Redacts patient identity, phone numbers, SSNs, and emails. (DETECT -> SANITIZE -> PASS)
    
    Returns:
        GuardrailResult indicating the final action ('pass', 'block', or 'sanitize')
        along with any sanitized_input or user-facing response message.
    """
    if not user_input or not user_input.strip():
        return GuardrailResult(
            triggered=False,
            guardrail="input_pipeline",
            action="pass",
            sanitized_input=user_input,
        )

    # 1. Critical Emergency Check (P0)
    emergency_res = check_emergency(user_input)
    if emergency_res.action == "block":
        return emergency_res

    # 2. Dosage & Prescription Blocker (P0)
    dosage_res = check_dosage(user_input)
    if dosage_res.action == "block":
        return dosage_res

    # 3. Prompt Injection & Jailbreak Blocker (P0)
    injection_res = check_injection(user_input)
    if injection_res.action == "block":
        return injection_res

    # 4. PII / PHI Sanitizer (P1)
    pii_res = check_and_sanitize_pii(user_input)
    if pii_res.action == "sanitize":
        return pii_res

    # All checks passed cleanly
    return GuardrailResult(
        triggered=False,
        guardrail="input_pipeline",
        action="pass",
        sanitized_input=user_input,
    )
