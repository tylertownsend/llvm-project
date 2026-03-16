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
class FixIt:
    message: str
    replacement: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int

    def to_dict(self) -> dict[str, object]:
        return {
            "message": self.message,
            "replacement": self.replacement,
            "start_line": self.start_line,
            "start_column": self.start_column,
            "end_line": self.end_line,
            "end_column": self.end_column,
        }


@dataclass(frozen=True)
class LintDiagnostic:
    code: str
    message: str
    path: str
    line: int
    column: int
    severity: str = "warning"
    fix: FixIt | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "code": self.code,
            "message": self.message,
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "severity": self.severity,
        }
        if self.fix is not None:
            payload["fix"] = self.fix.to_dict()
        return payload


@dataclass(frozen=True)
class LintResult:
    diagnostics: list[LintDiagnostic]
    applied_fixes: int = 0

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

_SAFE_INCLUDE_FIX_RE = re.compile(r'^(\s*)#\s*include\s*"([^"]+)"\s*$')


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


def _safe_fix_for_match(code: str, line_text: str, line_no: int) -> FixIt | None:
    if code != "CNXT9101":
        return None

    match = _SAFE_INCLUDE_FIX_RE.match(line_text)
    if match is None:
        return None

    indent, module_path = match.groups()
    return FixIt(
        message='replace textual include with cNxt import',
        replacement=f'{indent}import "{module_path}";',
        start_line=line_no,
        start_column=1,
        end_line=line_no,
        end_column=len(line_text) + 1,
    )


def _line_start_offsets(text: str) -> list[int]:
    offsets = [0]
    for idx, char in enumerate(text):
        if char == "\n":
            offsets.append(idx + 1)
    return offsets


def _offset_for_line_col(line_offsets: list[int], line: int, column: int) -> int:
    if line <= 0 or line > len(line_offsets):
        raise ValueError(f"invalid line: {line}")
    if column <= 0:
        raise ValueError(f"invalid column: {column}")
    return line_offsets[line - 1] + column - 1


def apply_safe_fixes(text: str, diagnostics: list[LintDiagnostic]) -> tuple[str, int]:
    fixes = [diag.fix for diag in diagnostics if diag.fix is not None]
    if not fixes:
        return text, 0

    line_offsets = _line_start_offsets(text)
    fix_ranges: list[tuple[int, int, FixIt]] = []
    for fix in fixes:
        assert fix is not None
        try:
            start = _offset_for_line_col(line_offsets, fix.start_line, fix.start_column)
            end = _offset_for_line_col(line_offsets, fix.end_line, fix.end_column)
        except ValueError:
            continue
        if end < start:
            continue
        fix_ranges.append((start, end, fix))

    applied = 0
    rewritten = text
    for start, end, fix in sorted(fix_ranges, key=lambda item: (item[0], item[1]), reverse=True):
        rewritten = rewritten[:start] + fix.replacement + rewritten[end:]
        applied += 1

    return rewritten, applied


def lint_text(text: str, path: str = "<input>") -> LintResult:
    masked = _mask_comments_and_strings(text)
    source_lines = text.splitlines()
    masked_lines = masked.splitlines()
    diagnostics: list[LintDiagnostic] = []

    for line_no, line in enumerate(masked_lines, start=1):
        source_line = source_lines[line_no - 1] if line_no - 1 < len(source_lines) else ""
        for rule in LINT_RULES:
            for match in rule.pattern.finditer(line):
                diagnostics.append(
                    LintDiagnostic(
                        code=rule.code,
                        message=rule.message,
                        path=path,
                        line=line_no,
                        column=match.start() + 1,
                        fix=_safe_fix_for_match(rule.code, source_line, line_no),
                    )
                )

    return LintResult(diagnostics=diagnostics)


def lint_file(path: Path | str, apply_fixes: bool = False) -> LintResult:
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
            ],
            applied_fixes=0,
        )

    original = source_path.read_text(encoding="utf-8")
    initial = lint_text(original, path=str(source_path))
    if not apply_fixes:
        return initial

    rewritten, applied = apply_safe_fixes(original, initial.diagnostics)
    if applied > 0 and rewritten != original:
        source_path.write_text(rewritten, encoding="utf-8")

    post = lint_text(rewritten, path=str(source_path))
    return LintResult(diagnostics=post.diagnostics, applied_fixes=applied)


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


def lint_paths(raw_paths: list[str], apply_fixes: bool = False) -> LintResult:
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
            ],
            applied_fixes=0,
        )

    diagnostics: list[LintDiagnostic] = []
    applied_fixes = 0
    for path in paths:
        result = lint_file(path, apply_fixes=apply_fixes)
        diagnostics.extend(result.diagnostics)
        applied_fixes += result.applied_fixes
    return LintResult(diagnostics=diagnostics, applied_fixes=applied_fixes)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint cNxt source files.")
    parser.add_argument("paths", nargs="+", help="source files or directories")
    parser.add_argument(
        "--apply-fixes",
        action="store_true",
        help="apply safe fix-its in place before reporting diagnostics",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(argv if argv is not None else sys.argv[1:])
    result = lint_paths(ns.paths, apply_fixes=ns.apply_fixes)
    payload = {
        "ok": result.ok,
        "applied-fixes": result.applied_fixes,
        "diagnostics": [diag.to_dict() for diag in result.diagnostics],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
