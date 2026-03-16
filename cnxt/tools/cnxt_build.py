#!/usr/bin/env python3
"""`cnxt build` baseline command for cNxt projects."""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import importlib.util
import json
from pathlib import Path
import shlex
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
_manifest_module = _load_module("cnxt_manifest_parser", _TOOLS_DIR / "manifest_parser.py")
_lockfile_module = _load_module("cnxt_lockfile_generator", _TOOLS_DIR / "lockfile_generator.py")
_fetch_module = _load_module("cnxt_package_fetcher", _TOOLS_DIR / "package_fetcher.py")
parse_manifest_file = _manifest_module.parse_manifest_file
write_lockfile = _lockfile_module.write_lockfile
fetch_packages = _fetch_module.fetch_packages


@dataclass(frozen=True)
class BuildDiagnostic:
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
class BuildArtifact:
    kind: str
    name: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "name": self.name, "path": self.path}


@dataclass(frozen=True)
class BuildResult:
    artifacts: list[BuildArtifact]
    diagnostics: list[BuildDiagnostic]
    compile_commands_path: str | None
    lockfile_path: str | None

    @property
    def ok(self) -> bool:
        return not self.diagnostics


def _profile_flags(profile: str) -> list[str]:
    if profile == "release":
        return ["-O2", "-DNDEBUG"]
    return ["-O0", "-g"]


def _manifest_diag_to_build(diag: Any) -> BuildDiagnostic:
    return BuildDiagnostic(code=diag.code, message=diag.message, path=diag.path)


def _derive_targets(manifest: dict[str, Any], manifest_path: Path) -> list[dict[str, str]]:
    package = manifest.get("package", {})
    package_name = package.get("name")
    if not isinstance(package_name, str):
        return []

    targets: list[dict[str, str]] = []
    raw_targets = manifest.get("targets")
    if isinstance(raw_targets, dict):
        raw_lib = raw_targets.get("lib")
        if isinstance(raw_lib, dict):
            path = raw_lib.get("path")
            if isinstance(path, str):
                targets.append({"kind": "lib", "name": package_name, "path": path})

        raw_bins = raw_targets.get("bin")
        if isinstance(raw_bins, list):
            for item in raw_bins:
                if not isinstance(item, dict):
                    continue
                name = item.get("name")
                path = item.get("path")
                if isinstance(name, str) and isinstance(path, str):
                    targets.append({"kind": "bin", "name": name, "path": path})

        raw_tests = raw_targets.get("test")
        if isinstance(raw_tests, list):
            for item in raw_tests:
                if not isinstance(item, dict):
                    continue
                name = item.get("name")
                path = item.get("path")
                if isinstance(name, str) and isinstance(path, str):
                    targets.append({"kind": "test", "name": name, "path": path})

        return targets

    default_main = manifest_path.parent / "src" / "main.cn"
    default_lib = manifest_path.parent / "src" / "lib.cn"
    if default_main.exists():
        targets.append(
            {"kind": "bin", "name": package_name, "path": default_main.relative_to(manifest_path.parent).as_posix()}
        )
    if default_lib.exists():
        targets.append(
            {"kind": "lib", "name": package_name, "path": default_lib.relative_to(manifest_path.parent).as_posix()}
        )
    return targets


def _build_commands_for_target(
    compiler: str,
    manifest_dir: Path,
    target_dir: Path,
    profile: str,
    target: dict[str, str],
) -> tuple[list[list[str]], list[BuildArtifact], list[dict[str, str]]]:
    source = (manifest_dir / target["path"]).resolve()
    obj_name = f"{target['kind']}-{target['name']}.o"
    obj_path = target_dir / obj_name
    compile_cmd = [
        compiler,
        "-x",
        "cnxt",
        "-std=cnxt1",
        *_profile_flags(profile),
        "-c",
        str(source),
        "-o",
        str(obj_path),
    ]
    commands = [compile_cmd]
    compile_entries = [
        {
            "directory": str(manifest_dir),
            "file": str(source),
            "command": shlex.join(compile_cmd),
        }
    ]

    artifacts: list[BuildArtifact] = []
    if target["kind"] == "bin":
        bin_path = target_dir / target["name"]
        link_cmd = [compiler, str(obj_path), "-o", str(bin_path)]
        commands.append(link_cmd)
        artifacts.append(BuildArtifact(kind="bin", name=target["name"], path=str(bin_path)))
    elif target["kind"] == "test":
        test_bin = target_dir / f"{target['name']}.test"
        link_cmd = [compiler, str(obj_path), "-o", str(test_bin)]
        commands.append(link_cmd)
        artifacts.append(BuildArtifact(kind="test", name=target["name"], path=str(test_bin)))
    else:
        artifacts.append(BuildArtifact(kind="lib", name=target["name"], path=str(obj_path)))

    return commands, artifacts, compile_entries


def _run_commands(commands: list[list[str]]) -> list[BuildDiagnostic]:
    diagnostics: list[BuildDiagnostic] = []
    for cmd in commands:
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError:
            diagnostics.append(
                BuildDiagnostic(
                    code="CNXT7004",
                    path=cmd[0],
                    message=f"compiler not found: {cmd[0]}",
                )
            )
            break
        except subprocess.CalledProcessError as exc:
            diagnostics.append(
                BuildDiagnostic(
                    code="CNXT7003",
                    path=cmd[-1] if cmd else "<command>",
                    message=f"build command failed: {' '.join(cmd)}\n{exc.stderr}",
                )
            )
            break
    return diagnostics


def run_build(
    root_manifest: Path | str,
    profile: str = "debug",
    dry_run: bool = False,
    skip_fetch: bool = False,
    registry: Path | str | None = None,
    cache_root: Path | str | None = None,
    compiler: str = "clang",
) -> BuildResult:
    manifest_path = Path(root_manifest).resolve()
    parse_result = parse_manifest_file(manifest_path)
    diagnostics: list[BuildDiagnostic] = [
        _manifest_diag_to_build(diag) for diag in parse_result.diagnostics
    ]
    if parse_result.manifest is None:
        diagnostics.append(
            BuildDiagnostic(
                code="CNXT7001",
                path=str(manifest_path),
                message=f"failed to parse manifest: {manifest_path}",
            )
        )
        return BuildResult(artifacts=[], diagnostics=diagnostics, compile_commands_path=None, lockfile_path=None)
    if diagnostics:
        return BuildResult(artifacts=[], diagnostics=diagnostics, compile_commands_path=None, lockfile_path=None)

    lockfile_result = write_lockfile(manifest_path)
    diagnostics.extend(_manifest_diag_to_build(diag) for diag in lockfile_result.diagnostics)
    if not lockfile_result.ok:
        diagnostics.append(
            BuildDiagnostic(
                code="CNXT7001",
                path=str(manifest_path.parent / "Cnxt.lock"),
                message="failed to generate lockfile for build",
            )
        )
        return BuildResult(artifacts=[], diagnostics=diagnostics, compile_commands_path=None, lockfile_path=None)

    if not skip_fetch:
        fetch_result = fetch_packages(
            manifest_path, lockfile_path=manifest_path.parent / "Cnxt.lock", registry=registry, cache_root=cache_root
        )
        diagnostics.extend(_manifest_diag_to_build(diag) for diag in fetch_result.diagnostics)
        if fetch_result.diagnostics:
            return BuildResult(
                artifacts=[],
                diagnostics=diagnostics,
                compile_commands_path=None,
                lockfile_path=str(manifest_path.parent / "Cnxt.lock"),
            )

    assert parse_result.manifest is not None
    targets = _derive_targets(parse_result.manifest, manifest_path)
    if not targets:
        diagnostics.append(
            BuildDiagnostic(
                code="CNXT7002",
                path=str(manifest_path),
                message="no build targets found (define [targets] or add src/main.cn/src/lib.cn)",
            )
        )
        return BuildResult(
            artifacts=[],
            diagnostics=diagnostics,
            compile_commands_path=None,
            lockfile_path=str(manifest_path.parent / "Cnxt.lock"),
        )

    profile_dir = manifest_path.parent / "target" / profile
    profile_dir.mkdir(parents=True, exist_ok=True)

    all_commands: list[list[str]] = []
    compile_entries: list[dict[str, str]] = []
    artifacts: list[BuildArtifact] = []
    for target in targets:
        target_commands, target_artifacts, target_compile_entries = _build_commands_for_target(
            compiler, manifest_path.parent, profile_dir, profile, target
        )
        all_commands.extend(target_commands)
        compile_entries.extend(target_compile_entries)
        artifacts.extend(target_artifacts)

    compile_entries.sort(key=lambda entry: entry["file"])
    compile_commands_path = manifest_path.parent / "compile_commands.json"
    compile_commands_path.write_text(
        json.dumps(compile_entries, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if not dry_run:
        diagnostics.extend(_run_commands(all_commands))

    return BuildResult(
        artifacts=artifacts,
        diagnostics=diagnostics,
        compile_commands_path=str(compile_commands_path),
        lockfile_path=str(manifest_path.parent / "Cnxt.lock"),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a cNxt package")
    parser.add_argument("manifest", type=Path, help="Path to root Cnxt.toml")
    parser.add_argument(
        "--profile",
        choices=("debug", "release"),
        default="debug",
        help="Build profile",
    )
    parser.add_argument("--dry-run", action="store_true", help="Plan build without invoking compiler")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip dependency fetch stage")
    parser.add_argument("--registry", type=str, default=None, help="Registry root path/URL")
    parser.add_argument("--cache-root", type=Path, default=None, help="Override cache root")
    parser.add_argument("--compiler", type=str, default="clang", help="Compiler executable")
    args = parser.parse_args(argv)

    result = run_build(
        args.manifest,
        profile=args.profile,
        dry_run=args.dry_run,
        skip_fetch=args.skip_fetch,
        registry=args.registry,
        cache_root=args.cache_root,
        compiler=args.compiler,
    )
    payload = {
        "ok": result.ok,
        "artifacts": [artifact.to_dict() for artifact in result.artifacts],
        "compile_commands_path": result.compile_commands_path,
        "lockfile_path": result.lockfile_path,
        "diagnostics": [diag.to_dict() for diag in result.diagnostics],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
