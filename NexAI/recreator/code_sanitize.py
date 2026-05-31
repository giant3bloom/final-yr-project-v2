"""Extract and validate Python-only code from LLM responses."""
from __future__ import annotations

import ast
import re


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    fence = re.match(r"^```(?:python)?\s*\n?(.*?)\n?```\s*$", text, re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    return re.sub(r"^```(?:python)?\s*", "", text).replace("```", "").strip()


def extract_controller_code(raw: str) -> str | None:
    """Keep only the MazeController Python block from LLM output."""
    raw = _strip_markdown_fences(raw)
    raw = raw.replace("###optimization-start", "").replace("###optimization-end", "")

    match = re.search(r"(class MazeController\b[\s\S]*)", raw)
    if not match:
        return None

    code = match.group(1).strip()

    # Drop trailing prose after the class (lines that fail parse from the tail)
    lines = code.splitlines()
    while lines:
        candidate = "\n".join(lines).strip()
        try:
            ast.parse(candidate)
            return candidate
        except SyntaxError:
            lines.pop()

    return None


def validate_controller_code(code: str) -> tuple[bool, str | None]:
    """Parse check + required API: __init__(maze,...), export() returns list."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, f"Invalid Python syntax: {exc}"

    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "MazeController"]
    if not classes:
        return False, "Missing class MazeController"

    cls = classes[0]
    methods = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
    if "__init__" not in methods or "export" not in methods:
        return False, "MazeController must define __init__ and export"

    prose_markers = (
        re.compile(r"^\s*\*\s"),
        re.compile(r"^Wait,", re.IGNORECASE),
        re.compile(r"^Goal:", re.IGNORECASE),
        re.compile(r"^The previous", re.IGNORECASE),
    )
    for line in code.splitlines():
        for pat in prose_markers:
            if pat.match(line):
                return False, "Response contains prose/markdown, not pure Python"

    return True, None
