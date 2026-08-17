# Guardrails/output/pipeline.py
from typing import List, Any
from .models import OutputGuardrailResult
from .safety import check_output_safety
from .faithfulness import check_faithfulness
from .disclaimer import apply_disclaimer


def run_output_guardrails(response_text: str, context_docs: List[Any] = None) -> OutputGuardrailResult:
    """
    Orchestrates all Output Guardrails in sequence:
    
    1. ☣️ Output Safety Scanner: Intercepts harmful DIY advice, toxic cures, or prescriptive dosage leaks.
    2. 🔎 Faithfulness Verifier: Enforces strict refusal when retrieval context is empty.
    3. ⚠️ Mandatory Disclaimer: Appends clinical disclaimer footer to verified answers.
    
    Returns:
        OutputGuardrailResult containing the safe, verified, and disclaimed output string.
    """
    if not response_text:
        return OutputGuardrailResult(
            passed=True,
            guardrail="output_pipeline",
            action="pass",
            output_text="",
        )

    context_docs = context_docs or []
    all_violations = []

    # Step 1: Harmful / Prescriptive Advice Scan (P0)
    safety_res = check_output_safety(response_text)
    if safety_res.action == "block":
        return safety_res

    # Step 2: Faithfulness & Grounding Check (P1)
    faithfulness_res = check_faithfulness(response_text, context_docs)
    current_text = faithfulness_res.output_text
    if faithfulness_res.violations:
        all_violations.extend(faithfulness_res.violations)

    # Step 3: Mandatory Medical Disclaimer Appender (P0)
    disclaimer_res = apply_disclaimer(current_text)
    final_text = disclaimer_res.output_text

    return OutputGuardrailResult(
        passed=True,
        guardrail="output_pipeline",
        action="modify" if final_text != response_text else "pass",
        reason="Output verified through safety, faithfulness, and disclaimer pipeline.",
        violations=all_violations,
        output_text=final_text,
    )
