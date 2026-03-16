#!/usr/bin/env python3
"""`cnxt test` baseline command for cNxt projects."""

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
_workspace_module = _load_module("cnxt_workspace_discovery", _TOOLS_DIR / "workspace_discovery.py")
run_build = _build_module.run_build
resolve_manifest_input = _workspace_module.resolve_manifest_input


@dataclass(frozen=True)
class TestDiagnostic:
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
class TestExecution:
    name: str
    path: str
    exit_code: int
    stdout: str
    stderr: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "status": self.status,
        }


@dataclass(frozen=True)
class TestResult:
    executions: list[TestExecution]
    diagnostics: list[TestDiagnostic]

    @property
    def ok(self) -> bool:
        return not self.diagnostics


def _to_test_diag(diag: Any) -> TestDiagnostic:
    return TestDiagnostic(code=diag.code, message=diag.message, path=diag.path)


def _discover_test_artifacts(manifest_path: Path, profile: str) -> list[Path]:
    target_dir = manifest_path.parent / "target" / profile
    if not target_dir.exists():
        return []
    return sorted(path for path in target_dir.glob("*.test") if path.is_file())


def run_tests(
    root_manifest: Path | str | None,
    profile: str = "debug",
    filter_text: str | None = None,
    skip_build: bool = False,
    skip_fetch: bool = False,
    registry: str | None = None,
    cache_root: Path | str | None = None,
    compiler: str = "clang",
) -> TestResult:
    discovery_result = resolve_manifest_input(root_manifest)
    diagnostics: list[TestDiagnostic] = [_to_test_diag(diag) for diag in discovery_result.diagnostics]
    if discovery_result.package_manifest is None:
        return TestResult(executions=[], diagnostics=diagnostics)

    manifest_path = Path(discovery_result.package_manifest).resolve()
    test_targets: list[tuple[str, Path]] = []

    if skip_build:
        for path in _discover_test_artifacts(manifest_path, profile):
            name = path.stem
            if filter_text and filter_text not in name:
                continue
            test_targets.append((name, path))
    else:
        build_result = run_build(
            manifest_path,
            profile=profile,
            dry_run=False,
            skip_fetch=skip_fetch,
            registry=registry,
            cache_root=cache_root,
            compiler=compiler,
        )
        diagnostics.extend(_to_test_diag(diag) for diag in build_result.diagnostics)
        if build_result.diagnostics:
            return TestResult(executions=[], diagnostics=diagnostics)

        for artifact in build_result.artifacts:
            if artifact.kind != "test":
                continue
            if filter_text and filter_text not in artifact.name:
                continue
            test_targets.append((artifact.name, Path(artifact.path)))

    if not test_targets:
        diagnostics.append(
            TestDiagnostic(
                code="CNXT7201",
                path=str(manifest_path),
                message="no test targets found",
            )
        )
        return TestResult(executions=[], diagnostics=diagnostics)

    executions: list[TestExecution] = []
    for name, path in test_targets:
        if not path.exists():
            diagnostics.append(
                TestDiagnostic(
                    code="CNXT7202",
                    path=str(path),
                    message=f"test binary not found: {path}",
                )
            )
            continue
        try:
            completed = subprocess.run(
                [str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
        except PermissionError:
            diagnostics.append(
                TestDiagnostic(
                    code="CNXT7202",
                    path=str(path),
                    message=f"test binary is not executable: {path}",
                )
            )
            continue
        except FileNotFoundError:
            diagnostics.append(
                TestDiagnostic(
                    code="CNXT7202",
                    path=str(path),
                    message=f"test binary not found: {path}",
                )
            )
            continue

        status = "passed" if completed.returncode == 0 else "failed"
        executions.append(
            TestExecution(
                name=name,
                path=str(path),
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                status=status,
            )
        )
        if completed.returncode != 0:
            diagnostics.append(
                TestDiagnostic(
                    code="CNXT7203",
                    path=str(path),
                    message=f"test '{name}' failed with exit code {completed.returncode}",
                )
            )

    executions.sort(key=lambda execution: execution.name)
    return TestResult(executions=executions, diagnostics=diagnostics)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and run cNxt tests")
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        default=None,
        help="Path to Cnxt.toml or project directory (default: current directory)",
    )
    parser.add_argument(
        "--profile",
        choices=("debug", "release"),
        default="debug",
        help="Build profile",
    )
    parser.add_argument("--filter", dest="filter_text", default=None, help="Only run tests matching text")
    parser.add_argument("--skip-build", action="store_true", help="Run existing test artifacts only")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip dependency fetch in build step")
    parser.add_argument("--registry", type=str, default=None, help="Registry root path/URL")
    parser.add_argument("--cache-root", type=Path, default=None, help="Override cache root")
    parser.add_argument("--compiler", type=str, default="clang", help="Compiler executable")
    args = parser.parse_args(argv)

    result = run_tests(
        args.manifest,
        profile=args.profile,
        filter_text=args.filter_text,
        skip_build=args.skip_build,
        skip_fetch=args.skip_fetch,
        registry=args.registry,
        cache_root=args.cache_root,
        compiler=args.compiler,
    )
    payload = {
        "ok": result.ok,
        "executions": [execution.to_dict() for execution in result.executions],
        "diagnostics": [diag.to_dict() for diag in result.diagnostics],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
