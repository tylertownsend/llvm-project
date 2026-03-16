#!/usr/bin/env python3
"""Deterministic lockfile generator for cNxt manifests."""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import importlib.util
import json
from pathlib import Path
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
_parser_module = _load_module("cnxt_manifest_parser", _TOOLS_DIR / "manifest_parser.py")
_graph_module = _load_module("cnxt_dependency_graph", _TOOLS_DIR / "dependency_graph.py")
_solver_module = _load_module("cnxt_version_solver", _TOOLS_DIR / "version_solver.py")
parse_manifest_file = _parser_module.parse_manifest_file
build_dependency_graph = _graph_module.build_dependency_graph
solve_versions = _solver_module.solve_versions


@dataclass(frozen=True)
class LockfileDiagnostic:
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
class LockfileGenerationResult:
    lockfile: dict[str, Any] | None
    diagnostics: list[LockfileDiagnostic]
    output_path: str | None = None

    @property
    def ok(self) -> bool:
        return not self.diagnostics and self.lockfile is not None


def _to_lock_diag(diag: Any) -> LockfileDiagnostic:
    return LockfileDiagnostic(code=diag.code, message=diag.message, path=diag.path)


def _relative_posix(path: Path, base: Path) -> str:
    resolved = path.resolve()
    base_resolved = base.resolve()
    try:
        return resolved.relative_to(base_resolved).as_posix()
    except ValueError:
        return resolved.as_posix()


def _resolve_dep_target_name(dep_name: str, dep_spec: Any, manifest_dir: Path) -> str:
    if not isinstance(dep_spec, dict):
        return dep_name
    package_override = dep_spec.get("package")
    if isinstance(package_override, str):
        return package_override
    dep_path = dep_spec.get("path")
    if not isinstance(dep_path, str):
        return dep_name
    candidate = (manifest_dir / dep_path).resolve()
    if candidate.is_dir():
        candidate = candidate / "Cnxt.toml"
    parsed = parse_manifest_file(candidate)
    if parsed.manifest is None:
        return dep_name
    package = parsed.manifest.get("package", {})
    package_name = package.get("name")
    if isinstance(package_name, str):
        return package_name
    return dep_name


def _normalize_dependency(dep_name: str, dep_spec: Any, manifest_dir: Path) -> dict[str, Any]:
    target_name = _resolve_dep_target_name(dep_name, dep_spec, manifest_dir)
    entry: dict[str, Any] = {"name": target_name}

    if isinstance(dep_spec, str):
        entry["source"] = "version"
        entry["requirement"] = dep_spec
        return entry

    if isinstance(dep_spec, dict):
        requirement = dep_spec.get("version")
        dep_path = dep_spec.get("path")
        dep_git = dep_spec.get("git")
        if isinstance(requirement, str):
            entry["source"] = "version"
            entry["requirement"] = requirement
        elif isinstance(dep_path, str):
            entry["source"] = "path"
            entry["path"] = dep_path
        elif isinstance(dep_git, str):
            entry["source"] = "git"
            entry["git"] = dep_git
            for ref_key in ("rev", "tag", "branch"):
                value = dep_spec.get(ref_key)
                if isinstance(value, str):
                    entry[ref_key] = value
        else:
            entry["source"] = "unknown"

        optional = dep_spec.get("optional")
        if isinstance(optional, bool) and optional:
            entry["optional"] = True
        features = dep_spec.get("features")
        if isinstance(features, list) and all(isinstance(item, str) for item in features):
            entry["features"] = sorted(features)
        return entry

    entry["source"] = "unknown"
    return entry


def _dependency_sort_key(dep: dict[str, Any]) -> tuple[str, ...]:
    return (
        str(dep.get("name", "")),
        str(dep.get("source", "")),
        str(dep.get("requirement", "")),
        str(dep.get("path", "")),
        str(dep.get("git", "")),
        str(dep.get("branch", "")),
        str(dep.get("tag", "")),
        str(dep.get("rev", "")),
    )


def generate_lockfile(root_manifest: Path | str) -> LockfileGenerationResult:
    root_manifest_path = Path(root_manifest).resolve()
    base_dir = root_manifest_path.parent
    solver = solve_versions(root_manifest_path)
    diagnostics = [_to_lock_diag(diag) for diag in solver.diagnostics]
    if diagnostics:
        return LockfileGenerationResult(lockfile=None, diagnostics=diagnostics)

    graph = build_dependency_graph(root_manifest_path)
    root_parsed = parse_manifest_file(root_manifest_path)
    if root_parsed.manifest is None:
        diagnostics.append(
            LockfileDiagnostic(
                code="CNXT4001",
                path=str(root_manifest_path),
                message=f"failed to parse root manifest: {root_manifest_path}",
            )
        )
        return LockfileGenerationResult(lockfile=None, diagnostics=diagnostics)

    root_package = root_parsed.manifest.get("package", {})
    root_name = root_package.get("name")
    if not isinstance(root_name, str):
        diagnostics.append(
            LockfileDiagnostic(
                code="CNXT4002",
                path="package.name",
                message="root package.name must be a string",
            )
        )
        return LockfileGenerationResult(lockfile=None, diagnostics=diagnostics)

    packages: list[dict[str, Any]] = []
    for package_name in sorted(graph.nodes):
        node = graph.nodes[package_name]
        manifest_path = Path(node.manifest_path)
        parsed = parse_manifest_file(manifest_path)
        if parsed.manifest is None:
            diagnostics.append(
                LockfileDiagnostic(
                    code="CNXT4001",
                    path=str(manifest_path),
                    message=f"failed to parse manifest: {manifest_path}",
                )
            )
            continue

        package = parsed.manifest.get("package", {})
        version = package.get("version")
        if not isinstance(version, str):
            diagnostics.append(
                LockfileDiagnostic(
                    code="CNXT4002",
                    path=f"{manifest_path}:package.version",
                    message=f"package '{package_name}' has invalid or missing package.version",
                )
            )
            continue

        dependencies: list[dict[str, Any]] = []
        deps = parsed.manifest.get("dependencies", {})
        if isinstance(deps, dict):
            for dep_name, dep_spec in deps.items():
                dependencies.append(
                    _normalize_dependency(dep_name, dep_spec, manifest_path.parent)
                )
        dependencies.sort(key=_dependency_sort_key)

        packages.append(
            {
                "name": package_name,
                "version": version,
                "manifest-path": _relative_posix(manifest_path, base_dir),
                "dependencies": dependencies,
            }
        )

    if diagnostics:
        return LockfileGenerationResult(lockfile=None, diagnostics=diagnostics)

    constraints = {
        package_name: sorted(requirements)
        for package_name, requirements in sorted(solver.constraints.items())
    }
    lockfile: dict[str, Any] = {
        "lockfile-version": 1,
        "root-manifest": _relative_posix(root_manifest_path, base_dir),
        "root-package": root_name,
        "packages": packages,
        "constraints": constraints,
    }
    return LockfileGenerationResult(lockfile=lockfile, diagnostics=[])


def render_lockfile(lockfile: dict[str, Any]) -> str:
    return json.dumps(lockfile, indent=2, sort_keys=True) + "\n"


def write_lockfile(
    root_manifest: Path | str, output_path: Path | str | None = None
) -> LockfileGenerationResult:
    result = generate_lockfile(root_manifest)
    if not result.ok or result.lockfile is None:
        return result

    root_manifest_path = Path(root_manifest).resolve()
    out_path = (
        Path(output_path).resolve()
        if output_path is not None
        else root_manifest_path.parent / "Cnxt.lock"
    )
    out_path.write_text(render_lockfile(result.lockfile), encoding="utf-8")
    return LockfileGenerationResult(
        lockfile=result.lockfile, diagnostics=[], output_path=str(out_path)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate deterministic cNxt lockfile from Cnxt.toml"
    )
    parser.add_argument("manifest", type=Path, help="Path to root Cnxt.toml")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output path for lockfile (default: <manifest-dir>/Cnxt.lock)",
    )
    args = parser.parse_args(argv)

    result = write_lockfile(args.manifest, args.output)
    payload: dict[str, Any] = {
        "ok": result.ok,
        "output_path": result.output_path,
        "lockfile": result.lockfile if result.ok else None,
        "diagnostics": [diag.to_dict() for diag in result.diagnostics],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
