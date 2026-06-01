"""Build the LLM optimization prompt from template + runtime feedback."""
from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any

PROMPT_FILE = Path(__file__).with_name("optimization_prompt.txt")

RUNTIME_ERROR_SECTION = """
RUNTIME FAIL (fix before optimizing): prior code crashed. See sandbox_error (headless) / demo_engine_error (Arcade child) in feedback. Next version must run clean — no repeat bugs.
"""

NULL_SCORE_SECTION = """
code score null — last run scored nothing. Fix/working controller first, then minimize steps.
"""


def format_feedback(feedback: Any) -> str:
    if not isinstance(feedback, dict):
        return str(feedback)

    lines = []
    for key, value in feedback.items():
        if value is None:
            lines.append(f"- {key}: null")
        elif isinstance(value, str) and "\n" in value:
            lines.append(f"- {key}:\n{textwrap.indent(value.strip(), '    ')}")
        else:
            lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def _load_template() -> str:
    return PROMPT_FILE.read_text(encoding="utf-8")


def build_optimization_prompt(block_code: str, feedback: Any) -> str:
    feedback_text = format_feedback(feedback)

    has_runtime_error = isinstance(feedback, dict) and (
        feedback.get("sandbox_error")
        or feedback.get("demo_engine_error")
        or feedback.get("llm_error")
    )
    score_is_null = isinstance(feedback, dict) and feedback.get("code score") is None

    error_section = RUNTIME_ERROR_SECTION if has_runtime_error else ""
    score_section = NULL_SCORE_SECTION if score_is_null else ""

    template = _load_template()
    return template.format(
        feedback_text=feedback_text,
        block_code=block_code,
        error_section=error_section,
        score_section=score_section,
    )
