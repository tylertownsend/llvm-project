#!/usr/bin/env python3
"""Workspace and project-root discovery helpers for cNxt commands."""

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
_manifest_module = _load_module("cnxt_manifest_parser", _TOOLS_DIR / "manifest_parser.py")
parse_manifest_file = _manifest_module.parse_manifest_file


@dataclass(frozen=True)
class WorkspaceDiagnostic:
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
class WorkspaceDiscoveryResult:
    package_manifest: str | None
    workspace_root_manifest: str | None
    diagnostics: list[WorkspaceDiagnostic]

    @property
    def ok(self) -> bool:
        return not self.diagnostics and self.package_manifest is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "package_manifest": self.package_manifest,
            "workspace_root_manifest": self.workspace_root_manifest,
            "diagnostics": [diag.to_dict() for diag in self.diagnostics],
        }


def _iter_ancestors(start_dir: Path) -> list[Path]:
    current = start_dir.resolve()
    ancestors = [current]
    ancestors.extend(current.parents)
    return ancestors


def _manifest_has_workspace_root(manifest_path: Path, package_manifest: Path) -> bool:
    parsed = parse_manifest_file(manifest_path)
    if parsed.manifest is None:
        return False
    workspace = parsed.manifest.get("workspace")
    if not isinstance(workspace, dict):
        return False
    members = workspace.get("members")
    workspace_dir = manifest_path.parent
    package_dir = package_manifest.parent
    if package_dir == workspace_dir:
        return True
    if not isinstance(members, list):
        return False
    for member in members:
        if not isinstance(member, str):
            continue
        candidate = (workspace_dir / member).resolve()
        if package_dir == candidate:
            return True
        try:
            package_dir.relative_to(candidate)
            return True
        except ValueError:
            continue
    return False


def discover_workspace(start: Path | str) -> WorkspaceDiscoveryResult:
    start_path = Path(start).resolve()
    start_dir = start_path if start_path.is_dir() else start_path.parent
    manifests: list[Path] = []
    for directory in _iter_ancestors(start_dir):
        manifest = directory / "Cnxt.toml"
        if manifest.exists():
            manifests.append(manifest)

    if not manifests:
        return WorkspaceDiscoveryResult(
            package_manifest=None,
            workspace_root_manifest=None,
            diagnostics=[
                WorkspaceDiagnostic(
                    code="CNXT8001",
                    path=str(start_dir),
                    message=f"no Cnxt.toml found from '{start_dir}' to filesystem root",
                )
            ],
        )

    package_manifest = manifests[0]
    workspace_manifest = package_manifest
    for manifest in reversed(manifests):
        if _manifest_has_workspace_root(manifest, package_manifest):
            workspace_manifest = manifest
            break

    return WorkspaceDiscoveryResult(
        package_manifest=str(package_manifest),
        workspace_root_manifest=str(workspace_manifest),
        diagnostics=[],
    )


def resolve_manifest_input(manifest_input: Path | str | None) -> WorkspaceDiscoveryResult:
    if manifest_input is None:
        return discover_workspace(Path.cwd())

    input_path = Path(manifest_input).resolve()
    if not input_path.exists():
        return WorkspaceDiscoveryResult(
            package_manifest=None,
            workspace_root_manifest=None,
            diagnostics=[
                WorkspaceDiagnostic(
                    code="CNXT8002",
                    path=str(input_path),
                    message=f"manifest path does not exist: {input_path}",
                )
            ],
        )

    if input_path.is_file():
        if input_path.name != "Cnxt.toml":
            return WorkspaceDiscoveryResult(
                package_manifest=None,
                workspace_root_manifest=None,
                diagnostics=[
                    WorkspaceDiagnostic(
                        code="CNXT8002",
                        path=str(input_path),
                        message=f"expected a Cnxt.toml file, got: {input_path.name}",
                    )
                ],
            )
        discovered = discover_workspace(input_path.parent)
        if discovered.package_manifest is None:
            return discovered
        return WorkspaceDiscoveryResult(
            package_manifest=str(input_path),
            workspace_root_manifest=discovered.workspace_root_manifest,
            diagnostics=discovered.diagnostics,
        )

    return discover_workspace(input_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Discover cNxt package/workspace root from a path")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        type=Path,
        help="File or directory to start discovery from (default: current directory)",
    )
    args = parser.parse_args(argv)

    result = resolve_manifest_input(args.path)
    json.dump(result.to_dict(), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
