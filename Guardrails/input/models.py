# Guardrails/input/models.py
from typing import Literal, Optional
from pydantic import BaseModel, Field


class GuardrailResult(BaseModel):
    """
    Standardized result contract for all guardrail checks.
    """
    triggered: bool = Field(..., description="Whether the guardrail condition was triggered.")
    guardrail: str = Field(..., description="Name/type of the guardrail (e.g. 'emergency', 'injection', 'pii').")
    action: Literal["pass", "block", "sanitize"] = Field(..., description="Action recommendation: 'pass', 'block', or 'sanitize'.")
    reason: Optional[str] = Field(default=None, description="Detailed category or reason for the trigger (useful for auditing/logging).")
    message: Optional[str] = Field(default=None, description="Pre-rendered safe message to return to the user if blocked.")
    sanitized_input: Optional[str] = Field(default=None, description="Sanitized/redacted query if action is 'sanitize'.")
