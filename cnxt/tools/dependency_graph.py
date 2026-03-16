#!/usr/bin/env python3
"""Dependency graph builder for cNxt manifests."""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


_PARSER_SPEC = importlib.util.spec_from_file_location(
    "cnxt_manifest_parser", Path(__file__).resolve().parent / "manifest_parser.py"
)
assert _PARSER_SPEC and _PARSER_SPEC.loader
_parser_module = importlib.util.module_from_spec(_PARSER_SPEC)
sys.modules[_PARSER_SPEC.name] = _parser_module
_PARSER_SPEC.loader.exec_module(_parser_module)
parse_manifest_file = _parser_module.parse_manifest_file


@dataclass(frozen=True)
class GraphDiagnostic:
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
class GraphNode:
    name: str
    manifest_path: str
    dependencies: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "manifest_path": self.manifest_path,
            "dependencies": self.dependencies,
        }


@dataclass(frozen=True)
class DependencyGraphResult:
    nodes: dict[str, GraphNode]
    edges: list[tuple[str, str]]
    diagnostics: list[GraphDiagnostic]

    @property
    def ok(self) -> bool:
        return not self.diagnostics


def _resolve_dep_manifest(base_dir: Path, raw_path: Any) -> Path | None:
    if not isinstance(raw_path, str):
        return None
    candidate = (base_dir / raw_path).resolve()
    if candidate.is_dir():
        candidate = candidate / "Cnxt.toml"
    return candidate


def build_dependency_graph(root_manifest: Path | str) -> DependencyGraphResult:
    root = Path(root_manifest).resolve()
    diagnostics: list[GraphDiagnostic] = []
    manifests: dict[Path, dict[str, Any]] = {}
    package_name_for_manifest: dict[Path, str] = {}
    path_edges: set[tuple[Path, Path]] = set()
    to_visit = [root]
    visited: set[Path] = set()

    while to_visit:
        current = to_visit.pop()
        if current in visited:
            continue
        visited.add(current)

        parsed = parse_manifest_file(current)
        if parsed.manifest is None:
            diagnostics.append(
                GraphDiagnostic(
                    code="CNXT2001",
                    path=str(current),
                    message=f"failed to parse manifest: {current}",
                )
            )
            for diag in parsed.diagnostics:
                diagnostics.append(
                    GraphDiagnostic(code=diag.code, path=diag.path, message=diag.message)
                )
            continue

        manifests[current] = parsed.manifest
        package = parsed.manifest.get("package", {})
        package_name = package.get("name")
        if isinstance(package_name, str):
            package_name_for_manifest[current] = package_name

        dependencies = parsed.manifest.get("dependencies", {})
        if not isinstance(dependencies, dict):
            continue
        for dep_name, dep_spec in dependencies.items():
            if not isinstance(dep_spec, dict) or "path" not in dep_spec:
                continue
            dep_manifest = _resolve_dep_manifest(current.parent, dep_spec.get("path"))
            if dep_manifest is None or not dep_manifest.exists():
                diagnostics.append(
                    GraphDiagnostic(
                        code="CNXT2002",
                        path=f"{current}:dependencies.{dep_name}.path",
                        message=f"path dependency manifest not found: {dep_spec.get('path')}",
                    )
                )
                continue
            path_edges.add((current, dep_manifest))
            to_visit.append(dep_manifest)

    by_name: dict[str, Path] = {}
    for manifest_path, package_name in package_name_for_manifest.items():
        existing = by_name.get(package_name)
        if existing is not None and existing != manifest_path:
            diagnostics.append(
                GraphDiagnostic(
                    code="CNXT2003",
                    path=str(manifest_path),
                    message=(
                        f"duplicate package name '{package_name}' in manifests "
                        f"{existing} and {manifest_path}"
                    ),
                )
            )
        else:
            by_name[package_name] = manifest_path

    adjacency: dict[Path, list[Path]] = {}
    for src, dst in path_edges:
        adjacency.setdefault(src, []).append(dst)
        adjacency.setdefault(dst, [])

    cycle_keys: set[tuple[str, ...]] = set()
    visiting: set[Path] = set()
    visited_cycle: set[Path] = set()
    stack: list[Path] = []

    def emit_cycle(cycle_nodes: list[Path]) -> None:
        cycle_names = [package_name_for_manifest.get(node, str(node)) for node in cycle_nodes]
        key = tuple(cycle_names)
        if key in cycle_keys:
            return
        cycle_keys.add(key)
        diagnostics.append(
            GraphDiagnostic(
                code="CNXT2004",
                path=str(cycle_nodes[0]),
                message=f"dependency cycle detected: {' -> '.join(cycle_names)}",
            )
        )

    def dfs(node: Path) -> None:
        visiting.add(node)
        stack.append(node)
        for nxt in adjacency.get(node, []):
            if nxt in visited_cycle:
                continue
            if nxt in visiting:
                idx = stack.index(nxt)
                emit_cycle(stack[idx:] + [nxt])
                continue
            dfs(nxt)
        stack.pop()
        visiting.remove(node)
        visited_cycle.add(node)

    for node in sorted(adjacency):
        if node not in visited_cycle:
            dfs(node)

    nodes: dict[str, GraphNode] = {}
    edges: list[tuple[str, str]] = []
    for src, dst in sorted(path_edges, key=lambda pair: (str(pair[0]), str(pair[1]))):
        src_name = package_name_for_manifest.get(src)
        dst_name = package_name_for_manifest.get(dst)
        if not src_name or not dst_name:
            continue
        edges.append((src_name, dst_name))

    deps_by_src: dict[str, list[str]] = {}
    for src_name, dst_name in edges:
        deps_by_src.setdefault(src_name, []).append(dst_name)
    for src_name in deps_by_src:
        deps_by_src[src_name] = sorted(set(deps_by_src[src_name]))

    for manifest_path, package_name in package_name_for_manifest.items():
        nodes[package_name] = GraphNode(
            name=package_name,
            manifest_path=str(manifest_path),
            dependencies=deps_by_src.get(package_name, []),
        )

    return DependencyGraphResult(nodes=nodes, edges=edges, diagnostics=diagnostics)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build cNxt local dependency graph")
    parser.add_argument("manifest", type=Path, help="Path to root Cnxt.toml")
    args = parser.parse_args(argv)

    result = build_dependency_graph(args.manifest)
    payload = {
        "ok": result.ok,
        "nodes": {name: node.to_dict() for name, node in sorted(result.nodes.items())},
        "edges": result.edges,
        "diagnostics": [diag.to_dict() for diag in result.diagnostics],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
