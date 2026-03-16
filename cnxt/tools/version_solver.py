#!/usr/bin/env python3
"""Version constraint solver for cNxt dependency manifests."""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import importlib.util
import json
from pathlib import Path
import re
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
parse_manifest_file = _parser_module.parse_manifest_file
build_dependency_graph = _graph_module.build_dependency_graph


VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
REQ_RE = re.compile(r"^(?:\^|~|>=|<=|>|<)?\d+\.\d+\.\d+$")


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    @staticmethod
    def parse(raw: str) -> Version | None:
        match = VERSION_RE.fullmatch(raw.strip())
        if not match:
            return None
        return Version(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    def as_string(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class RequirementRange:
    lower: Version | None
    lower_inclusive: bool
    upper: Version | None
    upper_inclusive: bool

    def intersect(self, other: RequirementRange) -> RequirementRange:
        lower = self.lower
        lower_inc = self.lower_inclusive
        if other.lower is not None and (lower is None or other.lower > lower):
            lower = other.lower
            lower_inc = other.lower_inclusive
        elif other.lower is not None and lower is not None and other.lower == lower:
            lower_inc = lower_inc and other.lower_inclusive

        upper = self.upper
        upper_inc = self.upper_inclusive
        if other.upper is not None and (upper is None or other.upper < upper):
            upper = other.upper
            upper_inc = other.upper_inclusive
        elif other.upper is not None and upper is not None and other.upper == upper:
            upper_inc = upper_inc and other.upper_inclusive

        return RequirementRange(lower, lower_inc, upper, upper_inc)

    def is_empty(self) -> bool:
        if self.lower is None or self.upper is None:
            return False
        if self.lower > self.upper:
            return True
        if self.lower == self.upper and not (self.lower_inclusive and self.upper_inclusive):
            return True
        return False

    def contains(self, version: Version) -> bool:
        if self.lower is not None:
            if version < self.lower or (version == self.lower and not self.lower_inclusive):
                return False
        if self.upper is not None:
            if version > self.upper or (version == self.upper and not self.upper_inclusive):
                return False
        return True


@dataclass(frozen=True)
class SolverDiagnostic:
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
class VersionSolverResult:
    diagnostics: list[SolverDiagnostic]
    constraints: dict[str, list[str]]

    @property
    def ok(self) -> bool:
        return not self.diagnostics


def parse_requirement_to_range(requirement: str) -> RequirementRange | None:
    req = requirement.strip()
    if not REQ_RE.fullmatch(req):
        return None

    op = ""
    version_str = req
    for candidate in (">=", "<=", ">", "<", "^", "~"):
        if req.startswith(candidate):
            op = candidate
            version_str = req[len(candidate) :]
            break

    version = Version.parse(version_str)
    if version is None:
        return None

    if op == "":
        return RequirementRange(version, True, version, True)
    if op == ">=":
        return RequirementRange(version, True, None, True)
    if op == ">":
        return RequirementRange(version, False, None, True)
    if op == "<=":
        return RequirementRange(None, True, version, True)
    if op == "<":
        return RequirementRange(None, True, version, False)
    if op == "^":
        if version.major > 0:
            upper = Version(version.major + 1, 0, 0)
        elif version.minor > 0:
            upper = Version(version.major, version.minor + 1, 0)
        else:
            upper = Version(version.major, version.minor, version.patch + 1)
        return RequirementRange(version, True, upper, False)
    if op == "~":
        upper = Version(version.major, version.minor + 1, 0)
        return RequirementRange(version, True, upper, False)
    return None


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


def solve_versions(root_manifest: Path | str) -> VersionSolverResult:
    graph = build_dependency_graph(root_manifest)
    diagnostics: list[SolverDiagnostic] = [
        SolverDiagnostic(code=diag.code, message=diag.message, path=diag.path)
        for diag in graph.diagnostics
    ]

    local_versions: dict[str, Version] = {}
    constraints: dict[str, list[str]] = {}

    for node in graph.nodes.values():
        manifest_path = Path(node.manifest_path)
        parsed = parse_manifest_file(manifest_path)
        if parsed.manifest is None:
            continue
        package = parsed.manifest.get("package", {})
        package_name = package.get("name")
        package_version = package.get("version")
        if isinstance(package_name, str) and isinstance(package_version, str):
            parsed_version = Version.parse(package_version)
            if parsed_version is not None:
                local_versions[package_name] = parsed_version

        deps = parsed.manifest.get("dependencies", {})
        if not isinstance(deps, dict):
            continue
        for dep_name, dep_spec in deps.items():
            requirement: str | None = None
            if isinstance(dep_spec, str):
                requirement = dep_spec
            elif isinstance(dep_spec, dict) and isinstance(dep_spec.get("version"), str):
                requirement = dep_spec["version"]
            if requirement is None:
                continue
            target_name = _resolve_dep_target_name(dep_name, dep_spec, manifest_path.parent)
            constraints.setdefault(target_name, []).append(requirement)

    for target_name, reqs in constraints.items():
        active_range: RequirementRange | None = None
        invalid = False
        for req in reqs:
            req_range = parse_requirement_to_range(req)
            if req_range is None:
                diagnostics.append(
                    SolverDiagnostic(
                        code="CNXT3003",
                        path=f"constraints.{target_name}",
                        message=f"unsupported version requirement '{req}'",
                    )
                )
                invalid = True
                continue
            if active_range is None:
                active_range = req_range
            else:
                active_range = active_range.intersect(req_range)

        if invalid or active_range is None:
            continue

        if active_range.is_empty():
            diagnostics.append(
                SolverDiagnostic(
                    code="CNXT3002",
                    path=f"constraints.{target_name}",
                    message=f"conflicting version requirements for '{target_name}': {', '.join(reqs)}",
                )
            )
            continue

        local = local_versions.get(target_name)
        if local is not None and not active_range.contains(local):
            diagnostics.append(
                SolverDiagnostic(
                    code="CNXT3001",
                    path=f"constraints.{target_name}",
                    message=(
                        f"local package '{target_name}' version {local.as_string()} "
                        f"does not satisfy constraints: {', '.join(reqs)}"
                    ),
                )
            )

    return VersionSolverResult(diagnostics=diagnostics, constraints=constraints)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Solve cNxt dependency version constraints")
    parser.add_argument("manifest", type=Path, help="Path to root Cnxt.toml")
    args = parser.parse_args(argv)

    result = solve_versions(args.manifest)
    payload = {
        "ok": result.ok,
        "constraints": result.constraints,
        "diagnostics": [diag.to_dict() for diag in result.diagnostics],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
