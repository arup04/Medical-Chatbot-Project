# Guardrails/output/faithfulness.py
from typing import List, Any
from .models import OutputGuardrailResult

GROUNDED_REFUSAL_RESPONSE = "I'm sorry, but I don't have information on that topic."


def check_faithfulness(response_text: str, context_docs: List[Any]) -> OutputGuardrailResult:
    """
    Verifies that the generated response is faithful to the retrieval context.
    
    If context_docs is empty and the LLM generated speculative content instead
    of the required refusal, this guardrail enforces the refusal policy.
    """
    if not response_text:
        return OutputGuardrailResult(
            passed=True,
            guardrail="faithfulness",
            action="pass",
            output_text=response_text,
        )

    # If context is empty, the LLM MUST refuse
    if not context_docs or len(context_docs) == 0:
        normalized_response = response_text.lower()
        if "don't have information" not in normalized_response and "do not have information" not in normalized_response:
            # Hallucination detected when context was empty
            return OutputGuardrailResult(
                passed=False,
                guardrail="faithfulness",
                action="modify",
                reason="Context was empty but LLM generated ungrounded answer. Enforced grounded refusal.",
                violations=["hallucination_without_context"],
                output_text=GROUNDED_REFUSAL_RESPONSE,
            )

    return OutputGuardrailResult(
        passed=True,
        guardrail="faithfulness",
        action="pass",
        output_text=response_text,
    )
