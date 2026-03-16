#!/usr/bin/env python3
"""Policy lints for cNxt source files."""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
from pathlib import Path
import re
import sys


@dataclass(frozen=True)
class LintDiagnostic:
    code: str
    message: str
    path: str
    line: int
    column: int
    severity: str = "warning"

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "message": self.message,
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class LintResult:
    diagnostics: list[LintDiagnostic]

    @property
    def ok(self) -> bool:
        return not self.diagnostics


@dataclass(frozen=True)
class LintRule:
    code: str
    pattern: re.Pattern[str]
    message: str


LINT_RULES: tuple[LintRule, ...] = (
    LintRule(
        code="CNXT9101",
        pattern=re.compile(r"^\s*#\s*include\b"),
        message="textual #include is not allowed in cNxt; use import/package dependencies",
    ),
    LintRule(
        code="CNXT9102",
        pattern=re.compile(r"\bfor\s*\("),
        message="C-style for(...) is not allowed; use cNxt for-in form",
    ),
    LintRule(
        code="CNXT9103",
        pattern=re.compile(r"\b(?:new|delete)\b"),
        message="manual heap operators are disallowed; use unique/shared/weak handles",
    ),
    LintRule(
        code="CNXT9104",
        pattern=re.compile(r"\b(?:try|catch|throw)\b"),
        message="exception constructs are disallowed in cNxt",
    ),
    LintRule(
        code="CNXT9105",
        pattern=re.compile(r"\btemplate\s*<"),
        message="template declarations are not part of cnxt1",
    ),
)


def _mask_comments_and_strings(text: str) -> str:
    chars = list(text)
    in_line_comment = False
    in_block_comment = False
    in_string: str | None = None
    escaped = False
    idx = 0

    while idx < len(chars):
        char = chars[idx]
        nxt = chars[idx + 1] if idx + 1 < len(chars) else ""

        if in_line_comment:
            if char == "\n":
                in_line_comment = False
            else:
                chars[idx] = " "
            idx += 1
            continue

        if in_block_comment:
            if char == "*" and nxt == "/":
                chars[idx] = " "
                chars[idx + 1] = " "
                in_block_comment = False
                idx += 2
            else:
                if char != "\n":
                    chars[idx] = " "
                idx += 1
            continue

        if in_string is not None:
            if char != "\n":
                chars[idx] = " "
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == in_string:
                in_string = None
            idx += 1
            continue

        if char == "/" and nxt == "/":
            chars[idx] = " "
            chars[idx + 1] = " "
            in_line_comment = True
            idx += 2
            continue

        if char == "/" and nxt == "*":
            chars[idx] = " "
            chars[idx + 1] = " "
            in_block_comment = True
            idx += 2
            continue

        if char in {'"', "'"}:
            chars[idx] = " "
            in_string = char
            escaped = False
            idx += 1
            continue

        idx += 1

    return "".join(chars)


def lint_text(text: str, path: str = "<input>") -> LintResult:
    masked = _mask_comments_and_strings(text)
    masked_lines = masked.splitlines()
    diagnostics: list[LintDiagnostic] = []

    for line_no, line in enumerate(masked_lines, start=1):
        for rule in LINT_RULES:
            for match in rule.pattern.finditer(line):
                diagnostics.append(
                    LintDiagnostic(
                        code=rule.code,
                        message=rule.message,
                        path=path,
                        line=line_no,
                        column=match.start() + 1,
                    )
                )

    return LintResult(diagnostics=diagnostics)


def lint_file(path: Path | str) -> LintResult:
    source_path = Path(path)
    if not source_path.exists():
        return LintResult(
            diagnostics=[
                LintDiagnostic(
                    code="CNXT9100",
                    message="source file does not exist",
                    path=str(source_path),
                    line=0,
                    column=0,
                    severity="error",
                )
            ]
        )
    return lint_text(source_path.read_text(encoding="utf-8"), path=str(source_path))


def _expand_input_paths(raw_paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in raw_paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.cn")))
            files.extend(sorted(path.rglob("*.cnxt")))
            files.extend(sorted(path.rglob("*.cni")))
            continue
        files.append(path)
    return files


def lint_paths(raw_paths: list[str]) -> LintResult:
    paths = _expand_input_paths(raw_paths)
    if not paths:
        return LintResult(
            diagnostics=[
                LintDiagnostic(
                    code="CNXT9100",
                    message="no input files found",
                    path="<input>",
                    line=0,
                    column=0,
                    severity="error",
                )
            ]
        )

    diagnostics: list[LintDiagnostic] = []
    for path in paths:
        diagnostics.extend(lint_file(path).diagnostics)
    return LintResult(diagnostics=diagnostics)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint cNxt source files.")
    parser.add_argument("paths", nargs="+", help="source files or directories")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(argv if argv is not None else sys.argv[1:])
    result = lint_paths(ns.paths)
    payload = {
        "ok": result.ok,
        "diagnostics": [diag.to_dict() for diag in result.diagnostics],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
