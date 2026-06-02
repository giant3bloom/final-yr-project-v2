"""Read/write the controller optimization block between marker lines."""
from __future__ import annotations

import re
from pathlib import Path

OPT_BLOCK = re.compile(
    r"(?P<start>###optimization-start)(?P<code>.*?)(?P<end>###optimization-end)",
    re.DOTALL,
)


def read_optimization_code(path: str | Path) -> str:
    script = Path(path).read_text(encoding="utf-8")
    match = OPT_BLOCK.search(script)
    if not match:
        raise ValueError("Optimization block not found in the script.")
    return match.group("code").strip()


def write_optimization_code(path: str | Path, code: str) -> None:
    """Replace only the region between markers; preserve prefix/suffix (e.g. __main__)."""
    file_path = Path(path)
    script = file_path.read_text(encoding="utf-8")
    match = OPT_BLOCK.search(script)
    if not match:
        raise ValueError("Optimization block not found in the script.")

    body = code.strip()
    new_middle = f"{match.group('start')}\n{body}\n{match.group('end')}"
    updated = script[: match.start()] + new_middle + script[match.end() :]

    tmp = file_path.with_suffix(file_path.suffix + ".tmp")
    tmp.write_text(updated, encoding="utf-8", newline="\n")
    tmp.replace(file_path)

    written = read_optimization_code(file_path)
    if written != body:
        raise RuntimeError("Optimization block on disk does not match what was written.")
