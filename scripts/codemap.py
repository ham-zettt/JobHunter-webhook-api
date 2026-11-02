#!/usr/bin/env python3
"""Generate docs/CODEMAP.md from app/ and scripts/ with the stdlib ast module."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "CODEMAP.md"
SKIP_DIRS = {"__pycache__", "data", "node_modules", ".venv", "graphify-out", "fixtures"}
SKIP_PREFIX = "_"

def _summary(doc: str | None) -> str:
    if not doc:
        return ""
    line = doc.strip().splitlines()[0].strip()
    return line[:120]

def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    args = ast.unparse(node.args)
    ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    return f"{prefix} {node.name}({args}){ret}"

def _module_doc(tree: ast.Module, path: Path) -> str:
    doc = ast.get_docstring(tree)
    return _summary(doc) or f"(no docstring) {path.name}"

def _file_lines(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    rel = path.relative_to(ROOT).as_posix()
    lines = [f"## `{rel}`", _module_doc(tree, path), ""]
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and not node.name.startswith(SKIP_PREFIX):
            bases = ", ".join(ast.unparse(b) for b in node.bases)
            head = f"`class {node.name}`" + (f" ({bases})" if bases else "")
            summary = _summary(ast.get_docstring(node))
            lines.append(f"- {head}" + (f" — {summary}" if summary else ""))
            for item in node.body:
                if (
                    isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and not item.name.startswith(SKIP_PREFIX)
                ):
                    summary = _summary(ast.get_docstring(item))
                    lines.append(
                        f"  - `{_signature(item)}`" + (f" — {summary}" if summary else "")
                    )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith(
            SKIP_PREFIX
        ):
            summary = _summary(ast.get_docstring(node))
            lines.append(f"- `{_signature(node)}`" + (f" — {summary}" if summary else ""))
    lines.append("")
    return lines

def main() -> None:
    files = []
    for folder in ("app", "scripts"):
        for path in sorted((ROOT / folder).rglob("*.py")):
            if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
                continue
            files.append(path)

    lines = [
        "# CODEMAP",
        "",
        "Dihasilkan otomatis oleh `python scripts/codemap.py`. Jangan edit manual.",
        "Hanya simbol publik; lihat file sumber untuk detail.",
        "",
    ]
    for path in files:
        lines.extend(_file_lines(path))
    OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(files)} files, {len(lines)} lines")

if __name__ == "__main__":
    main()
