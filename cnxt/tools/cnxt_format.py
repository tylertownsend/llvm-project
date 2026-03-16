#!/usr/bin/env python3
"""Baseline formatter profile and command for cNxt sources."""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


BASELINE_PROFILE = "baseline"
BASELINE_STYLE = (
    "{BasedOnStyle: LLVM, IndentWidth: 2, ContinuationIndentWidth: 4, "
    "ColumnLimit: 100, BreakBeforeBraces: Stroustrup, "
    "AllowShortFunctionsOnASingleLine: Empty, PointerAlignment: Left, "
    "SortIncludes: Never}"
)


@dataclass(frozen=True)
class FormatDiagnostic:
    code: str
    message: str
    path: str
    severity: str = "error"

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
            "path": self.path,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class FormatResult:
    text: str | None
    diagnostics: list[FormatDiagnostic]
    path: str
    changed: bool
    profile: str

    @property
    def ok(self) -> bool:
        return not self.diagnostics


def baseline_style() -> str:
    return BASELINE_STYLE


def resolve_clang_format(explicit_binary: str | None = None) -> str | None:
    if explicit_binary:
        return explicit_binary

    env_binary = os.environ.get("CNXT_CLANG_FORMAT")
    if env_binary:
        return env_binary

    return shutil.which("clang-format")


def _diag(code: str, path: str, message: str) -> FormatResult:
    return FormatResult(
        text=None,
        diagnostics=[FormatDiagnostic(code=code, path=path, message=message)],
        path=path,
        changed=False,
        profile=BASELINE_PROFILE,
    )


def format_text(
    source_text: str,
    *,
    filename: str = "input.cn",
    profile: str = BASELINE_PROFILE,
    clang_format: str | None = None,
) -> FormatResult:
    if profile != BASELINE_PROFILE:
        return _diag("CNXT9001", filename, f"unsupported formatter profile '{profile}'")

    formatter = resolve_clang_format(clang_format)
    if formatter is None:
        return _diag("CNXT9002", filename, "clang-format binary not found")

    cmd = [
        formatter,
        "--assume-filename",
        filename,
        f"--style={baseline_style()}",
    ]
    try:
        completed = subprocess.run(
            cmd,
            input=source_text,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        return _diag("CNXT9002", filename, f"clang-format binary not found: {formatter}")
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip()
        details = stderr if stderr else "no stderr output"
        return _diag("CNXT9003", filename, f"formatter execution failed: {details}")

    formatted = completed.stdout
    return FormatResult(
        text=formatted,
        diagnostics=[],
        path=filename,
        changed=formatted != source_text,
        profile=profile,
    )


def format_file(
    source_path: Path | str,
    *,
    write: bool = False,
    check: bool = False,
    profile: str = BASELINE_PROFILE,
    clang_format: str | None = None,
) -> FormatResult:
    path = Path(source_path)
    if not path.exists():
        return _diag("CNXT9004", str(path), "source file does not exist")

    original = path.read_text(encoding="utf-8")
    result = format_text(
        original,
        filename=str(path),
        profile=profile,
        clang_format=clang_format,
    )
    if not result.ok:
        return result

    assert result.text is not None
    diagnostics: list[FormatDiagnostic] = []
    if check and result.changed:
        diagnostics.append(
            FormatDiagnostic(
                code="CNXT9005",
                path=str(path),
                message="file is not formatted with cNxt baseline profile",
            )
        )
    if write and result.changed and not check:
        path.write_text(result.text, encoding="utf-8")

    return FormatResult(
        text=result.text,
        diagnostics=diagnostics,
        path=str(path),
        changed=result.changed,
        profile=profile,
    )


def _expand_input_paths(inputs: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.cn")))
            files.extend(sorted(path.rglob("*.cnxt")))
            files.extend(sorted(path.rglob("*.cni")))
            continue
        files.append(path)
    return files


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Format cNxt sources.")
    parser.add_argument("paths", nargs="+", help="source files or directories")
    parser.add_argument("--write", action="store_true", help="write formatted output back to files")
    parser.add_argument("--check", action="store_true", help="report files that need formatting")
    parser.add_argument("--profile", default=BASELINE_PROFILE, help="formatter profile to use")
    parser.add_argument("--clang-format", dest="clang_format", default=None, help="path to clang-format binary")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(argv if argv is not None else sys.argv[1:])
    files = _expand_input_paths(ns.paths)
    if not files:
        print(
            json.dumps(
                {
                    "diagnostics": [
                        {
                            "code": "CNXT9004",
                            "path": "<input>",
                            "message": "no input files found",
                            "severity": "error",
                        }
                    ],
                    "ok": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    diagnostics: list[FormatDiagnostic] = []
    changed_paths: list[str] = []
    for path in files:
        result = format_file(
            path,
            write=ns.write,
            check=ns.check,
            profile=ns.profile,
            clang_format=ns.clang_format,
        )
        diagnostics.extend(result.diagnostics)
        if result.changed:
            changed_paths.append(result.path)
        if not ns.write and not ns.check and result.ok and result.text is not None:
            print(result.text, end="")

    payload = {
        "ok": not diagnostics,
        "profile": ns.profile,
        "changed": changed_paths,
        "diagnostics": [diag.to_dict() for diag in diagnostics],
    }
    if ns.write or ns.check:
        print(json.dumps(payload, indent=2, sort_keys=True))

    return 0 if not diagnostics else 1


if __name__ == "__main__":
    raise SystemExit(main())
