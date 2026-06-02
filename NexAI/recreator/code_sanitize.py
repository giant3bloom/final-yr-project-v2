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


def _maze_controller_class(tree: ast.Module) -> ast.ClassDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "MazeController":
            return node
    return None


def _export_has_return(cls: ast.ClassDef) -> bool:
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == "export":
            return any(isinstance(n, ast.Return) for n in ast.walk(node))
    return False


def extract_controller_code(raw: str) -> str | None:
    """Keep only the MazeController Python block from LLM output."""
    raw = _strip_markdown_fences(raw)
    raw = raw.replace("###optimization-start", "").replace("###optimization-end", "")

    # Prefer full block (imports + class); fall back to class-only.
    match = re.search(
        r"^((?:[ \t]*(?:from|import)\s+.+$\n?)+)?(class MazeController\b[\s\S]*)",
        raw,
        re.MULTILINE,
    )
    if not match:
        return None

    code = (match.group(1) or "") + match.group(2)
    code = code.strip()

    lines = code.splitlines()
    while lines:
        candidate = "\n".join(lines).strip()
        try:
            tree = ast.parse(candidate)
        except SyntaxError:
            lines.pop()
            continue
        cls = _maze_controller_class(tree)
        if cls and _export_has_return(cls):
            return candidate
        lines.pop()

    return None


def _dry_run_controller(code: str) -> tuple[bool, str | None]:
    namespace: dict = {}
    try:
        exec(compile(code, "<optimization_block>", "exec"), namespace, namespace)
    except Exception as exc:
        return False, f"Block exec failed: {exc}"

    controller_cls = namespace.get("MazeController")
    if controller_cls is None:
        return False, "MazeController not defined after exec"

    try:
        import numpy as np

        maze = np.zeros((21, 21), dtype=int)
        ctrl = controller_cls(maze, start=(0, 0), max_steps=50)
        moves = ctrl.export()
    except Exception as exc:
        return False, f"MazeController dry-run failed: {exc}"

    if not isinstance(moves, list):
        return False, "export() must return a list"
    if len(moves) == 0:
        return False, "export() returned no moves"
    for move in moves:
        if move not in ("up", "down", "left", "right"):
            return False, f"Invalid move: {move!r}"

    from demo_engine.discovery import simulate_discovery

    discovered = simulate_discovery(maze, moves, start=(0, 0))
    if int((discovered != -1).sum()) < 20:
        return False, "export() explores too little of the maze (incomplete path)"

    return True, None


def validate_controller_code(code: str) -> tuple[bool, str | None]:
    """Parse check + required API: __init__(maze,...), export() returns list."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, f"Invalid Python syntax: {exc}"

    cls = _maze_controller_class(tree)
    if cls is None:
        return False, "Missing class MazeController"

    methods = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
    if "__init__" not in methods or "export" not in methods:
        return False, "MazeController must define __init__ and export"
    if not _export_has_return(cls):
        return False, "export() must contain a return statement (complete implementation)"

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

    return _dry_run_controller(code)
