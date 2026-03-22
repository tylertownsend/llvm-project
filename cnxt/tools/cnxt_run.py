#!/usr/bin/env python3
"""`cnxt run` baseline command for cNxt projects."""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_TOOLS_DIR = Path(__file__).resolve().parent
_build_module = _load_module("cnxt_build", _TOOLS_DIR / "cnxt_build.py")
_manifest_module = _load_module("cnxt_manifest_parser", _TOOLS_DIR / "manifest_parser.py")
_workspace_module = _load_module("cnxt_workspace_discovery", _TOOLS_DIR / "workspace_discovery.py")
run_build = _build_module.run_build
parse_manifest_file = _manifest_module.parse_manifest_file
resolve_manifest_input = _workspace_module.resolve_manifest_input


@dataclass(frozen=True)
class RunDiagnostic:
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
class RunResult:
    exit_code: int | None
    stdout: str
    stderr: str
    binary_path: str | None
    diagnostics: list[RunDiagnostic]

    @property
    def ok(self) -> bool:
        return not self.diagnostics and self.exit_code == 0


def _to_run_diag(diag: Any) -> RunDiagnostic:
    return RunDiagnostic(code=diag.code, message=diag.message, path=diag.path)


def _default_binary_name(manifest_path: Path) -> str | None:
    parsed = parse_manifest_file(manifest_path)
    manifest = parsed.manifest
    if manifest is None:
        return None
    package = manifest.get("package", {})
    name = package.get("name")
    return name if isinstance(name, str) else None


def _select_binary_from_build(
    artifacts: list[Any], bin_name: str | None
) -> tuple[str | None, list[RunDiagnostic]]:
    diagnostics: list[RunDiagnostic] = []
    binaries = [artifact for artifact in artifacts if getattr(artifact, "kind", None) == "bin"]
    if not binaries:
        diagnostics.append(
            RunDiagnostic(
                code="CNXT7102",
                path="target",
                message="no binary target available to run",
            )
        )
        return None, diagnostics

    if bin_name is None:
        binaries.sort(key=lambda artifact: str(getattr(artifact, "name", "")))
        return str(getattr(binaries[0], "path")), diagnostics

    for artifact in binaries:
        if getattr(artifact, "name", None) == bin_name:
            return str(getattr(artifact, "path")), diagnostics

    diagnostics.append(
        RunDiagnostic(
            code="CNXT7103",
            path="target",
            message=f"binary target '{bin_name}' was not built",
        )
    )
    return None, diagnostics


def run_package(
    root_manifest: Path | str | None,
    run_args: list[str] | None = None,
    bin_name: str | None = None,
    profile: str = "debug",
    skip_build: bool = False,
    skip_fetch: bool = False,
    locked: bool = False,
    registry: str | None = None,
    cache_root: Path | str | None = None,
    compiler: str = "clang++",
) -> RunResult:
    discovery_result = resolve_manifest_input(root_manifest)
    diagnostics: list[RunDiagnostic] = [_to_run_diag(diag) for diag in discovery_result.diagnostics]
    if discovery_result.package_manifest is None:
        return RunResult(
            exit_code=None, stdout="", stderr="", binary_path=None, diagnostics=diagnostics
        )

    manifest_path = Path(discovery_result.package_manifest).resolve()
    args = run_args if run_args is not None else []
    binary_path: str | None = None

    if skip_build:
        selected = bin_name if bin_name is not None else _default_binary_name(manifest_path)
        if not selected:
            diagnostics.append(
                RunDiagnostic(
                    code="CNXT7101",
                    path=str(manifest_path),
                    message="unable to determine binary name; set --bin",
                )
            )
            return RunResult(
                exit_code=None, stdout="", stderr="", binary_path=None, diagnostics=diagnostics
            )
        candidate = manifest_path.parent / "target" / profile / selected
        if not candidate.exists():
            diagnostics.append(
                RunDiagnostic(
                    code="CNXT7102",
                    path=str(candidate),
                    message=f"binary not found: {candidate}",
                )
            )
            return RunResult(
                exit_code=None, stdout="", stderr="", binary_path=None, diagnostics=diagnostics
            )
        binary_path = str(candidate)
    else:
        build_result = run_build(
            manifest_path,
            profile=profile,
            dry_run=False,
            skip_fetch=skip_fetch,
            locked=locked,
            registry=registry,
            cache_root=cache_root,
            compiler=compiler,
        )
        diagnostics.extend(_to_run_diag(diag) for diag in build_result.diagnostics)
        if build_result.diagnostics:
            return RunResult(
                exit_code=None, stdout="", stderr="", binary_path=None, diagnostics=diagnostics
            )
        selected, select_diags = _select_binary_from_build(build_result.artifacts, bin_name)
        diagnostics.extend(select_diags)
        if selected is None:
            return RunResult(
                exit_code=None, stdout="", stderr="", binary_path=None, diagnostics=diagnostics
            )
        binary_path = selected

    try:
        completed = subprocess.run(
            [binary_path, *args],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        diagnostics.append(
            RunDiagnostic(
                code="CNXT7102",
                path=str(binary_path),
                message=f"binary not found: {binary_path}",
            )
        )
        return RunResult(
            exit_code=None, stdout="", stderr="", binary_path=binary_path, diagnostics=diagnostics
        )
    except PermissionError:
        diagnostics.append(
            RunDiagnostic(
                code="CNXT7104",
                path=str(binary_path),
                message=f"binary is not executable: {binary_path}",
            )
        )
        return RunResult(
            exit_code=None, stdout="", stderr="", binary_path=binary_path, diagnostics=diagnostics
        )

    if completed.returncode != 0:
        diagnostics.append(
            RunDiagnostic(
                code="CNXT7104",
                path=str(binary_path),
                message=f"binary exited with non-zero status: {completed.returncode}",
            )
        )

    return RunResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        binary_path=binary_path,
        diagnostics=diagnostics,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and run a cNxt package")
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        default=None,
        help="Path to Cnxt.toml or project directory (default: current directory)",
    )
    parser.add_argument("--bin", dest="bin_name", default=None, help="Binary target name")
    parser.add_argument(
        "--profile",
        choices=("debug", "release"),
        default="debug",
        help="Build profile",
    )
    parser.add_argument("--skip-build", action="store_true", help="Run existing artifact only")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip dependency fetch in build step")
    parser.add_argument("--locked", action="store_true", help="Replay existing lockfile without regenerating")
    parser.add_argument("--registry", type=str, default=None, help="Registry root path/URL")
    parser.add_argument("--cache-root", type=Path, default=None, help="Override cache root")
    parser.add_argument("--compiler", type=str, default="clang++", help="Compiler executable")
    parser.add_argument("program_args", nargs=argparse.REMAINDER, help="Arguments for the program")
    args = parser.parse_args(argv)

    program_args = args.program_args
    if program_args and program_args[0] == "--":
        program_args = program_args[1:]

    result = run_package(
        args.manifest,
        run_args=program_args,
        bin_name=args.bin_name,
        profile=args.profile,
        skip_build=args.skip_build,
        skip_fetch=args.skip_fetch,
        locked=args.locked,
        registry=args.registry,
        cache_root=args.cache_root,
        compiler=args.compiler,
    )
    payload = {
        "ok": result.ok,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "binary_path": result.binary_path,
        "diagnostics": [diag.to_dict() for diag in result.diagnostics],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
