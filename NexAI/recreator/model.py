import os
import re
import textwrap
import time
from typing import Any

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from config import CONTROLLER_PATH, GEMINI_MODEL, GEMINI_THINKING_BUDGET, MAX_LLM_RETRIES
from NexAI.dynamic.status import log_message
from NexAI.recreator.block_io import read_optimization_code, write_optimization_code
from NexAI.recreator.code_sanitize import extract_controller_code, validate_controller_code
from NexAI.recreator.prompt import build_optimization_prompt, format_feedback


class AdaptiveMazeBlockOptimizer:
    def __init__(self, api_key: str, model_name: str | None = None):
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        model_name = model_name or GEMINI_MODEL
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self._generation_config = self._build_generation_config(model_name)
        self.last_error: str | None = None
        print(f"Using model: {model_name}")

    @staticmethod
    def _build_generation_config(model_name: str) -> dict | None:
        # thinking_budget only applies to Gemini 2.5; Gemma rejects it (400 error)
        if not model_name.startswith("gemini-2.5"):
            return None
        return {"thinking_budget": GEMINI_THINKING_BUDGET}

    @staticmethod
    def _parse_retry_seconds(error_text: str) -> int | None:
        match = re.search(r"retry in (\d+(?:\.\d+)?)s", error_text, re.IGNORECASE)
        if match:
            return max(1, int(float(match.group(1))))
        match = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", error_text)
        if match:
            return int(match.group(1))
        return None

    def _prepare_prompt(self, block_code: str, feedback: Any) -> str:
        log_message("prompt-generation", True, phase="llm")
        prompt = build_optimization_prompt(block_code, feedback)
        print(f"main code-generation feed\n{format_feedback(feedback)}")
        return prompt

    @staticmethod
    def _extract_text(response) -> str:
        try:
            text = response.text
            if text:
                return text.strip()
        except (ValueError, AttributeError):
            pass

        chunks: list[str] = []
        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            if not content:
                continue
            for part in getattr(content, "parts", []) or []:
                part_text = getattr(part, "text", None)
                if part_text:
                    chunks.append(part_text)
        return "".join(chunks).strip()

    def optimize_block(
        self,
        feedback: Any = None,
        script_path: str | os.PathLike | None = None,
    ) -> bool:
        if feedback is None:
            feedback = {"code score": None}

        try:
            return self._optimize_block_impl(feedback, script_path)
        except Exception as exc:
            log_message(
                "code-generation crashed",
                False,
                phase="llm",
                score=None,
                error=str(exc),
            )
            return False

    def _optimize_block_impl(
        self,
        feedback: Any,
        script_path: str | os.PathLike | None = None,
    ) -> bool:

        script_path = script_path or CONTROLLER_PATH
        cleaned_code = read_optimization_code(script_path)
        prompt = self._prepare_prompt(cleaned_code, feedback)
        self.last_error = None

        optimized_code = None
        last_error = ""

        for attempt in range(1, MAX_LLM_RETRIES + 1):
            try:
                kwargs: dict[str, Any] = {}
                if self._generation_config:
                    kwargs["generation_config"] = self._generation_config
                response = self.model.generate_content(prompt, **kwargs)
                optimized_code = self._extract_text(response)
                break
            except google_exceptions.ResourceExhausted as exc:
                last_error = str(exc)
                wait = self._parse_retry_seconds(last_error) or 60
                log_message(
                    f"LLM quota exceeded (attempt {attempt}/{MAX_LLM_RETRIES})",
                    False,
                    phase="llm",
                    score=None,
                    error=last_error[:500],
                )
                if attempt < MAX_LLM_RETRIES:
                    print(f"Waiting {wait}s before retry...")
                    time.sleep(wait)
                else:
                    print(
                        "Gemini API quota exhausted. Check billing/plan at "
                        "https://ai.google.dev/gemini-api/docs/rate-limits"
                    )
                    return False
            except Exception as exc:
                last_error = str(exc)
                log_message(
                    "LLM request failed",
                    False,
                    phase="llm",
                    score=None,
                    error=last_error,
                )
                return False

        if not optimized_code:
            log_message(
                "LLM returned empty response",
                False,
                phase="llm",
                score=None,
                error=last_error or "empty response",
            )
            return False

        extracted = extract_controller_code(optimized_code)
        if not extracted:
            log_message(
                "LLM output is not valid Python (no MazeController class)",
                False,
                phase="llm",
                score=None,
                error="Response contained prose/markdown instead of Python code",
            )
            return False

        ok, err = validate_controller_code(extracted)
        if not ok:
            self.last_error = err or "validation failed"
            log_message(
                "LLM code failed validation",
                False,
                phase="llm",
                score=None,
                error=self.last_error,
            )
            return False

        try:
            write_optimization_code(script_path, extracted)
        except Exception as exc:
            self.last_error = str(exc)
            log_message(
                "Failed to write controller block",
                False,
                phase="llm",
                score=None,
                error=self.last_error,
            )
            return False

        return True
