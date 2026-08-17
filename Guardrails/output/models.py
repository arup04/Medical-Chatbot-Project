# Guardrails/output/models.py
from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class OutputGuardrailResult(BaseModel):
    """
    Standardized contract for output guardrail evaluations.
    """
    passed: bool = Field(..., description="Whether the output passed all output safety and quality checks.")
    guardrail: str = Field(..., description="Name of the output guardrail (e.g. 'disclaimer', 'safety', 'faithfulness', 'output_pipeline').")
    action: Literal["pass", "block", "modify"] = Field(..., description="Action: 'pass' (unchanged), 'block' (blocked/fallback), or 'modify' (e.g. disclaimer appended).")
    reason: Optional[str] = Field(default=None, description="Detailed explanation if modified or blocked.")
    output_text: str = Field(..., description="Final processed output string.")
    violations: List[str] = Field(default_factory=list, description="List of detected policy violations or flags.")
