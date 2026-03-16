#!/usr/bin/env python3
"""Local cache layout planning for downloaded cNxt packages."""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


_SLUG_RE = re.compile(r"[^a-zA-Z0-9._-]+")


@dataclass(frozen=True)
class CacheDiagnostic:
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
class CacheLayout:
    root: str
    registry_packages: str
    git_checkouts: str
    git_sources: str
    temp: str
    locks: str

    def to_dict(self) -> dict[str, str]:
        return {
            "root": self.root,
            "registry_packages": self.registry_packages,
            "git_checkouts": self.git_checkouts,
            "git_sources": self.git_sources,
            "temp": self.temp,
            "locks": self.locks,
        }


@dataclass(frozen=True)
class CacheEntry:
    source: str
    package: str
    key: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "package": self.package,
            "key": self.key,
            "path": self.path,
        }


@dataclass(frozen=True)
class CachePlanResult:
    layout: CacheLayout
    entries: list[CacheEntry]
    diagnostics: list[CacheDiagnostic]

    @property
    def ok(self) -> bool:
        return not self.diagnostics


def _slug(text: str) -> str:
    lowered = text.strip().lower()
    slug = _SLUG_RE.sub("-", lowered).strip("-")
    return slug or "item"


def _stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def compute_cache_root(root_manifest: Path | str, cache_root: Path | str | None = None) -> Path:
    if cache_root is not None:
        return Path(cache_root).resolve()
    return Path(root_manifest).resolve().parent / ".cnxt" / "cache"


def build_cache_layout(root_manifest: Path | str, cache_root: Path | str | None = None) -> CacheLayout:
    root = compute_cache_root(root_manifest, cache_root)
    return CacheLayout(
        root=str(root),
        registry_packages=str(root / "registry" / "packages"),
        git_checkouts=str(root / "git" / "checkouts"),
        git_sources=str(root / "git" / "sources"),
        temp=str(root / "tmp"),
        locks=str(root / "locks"),
    )


def initialize_cache_layout(root_manifest: Path | str, cache_root: Path | str | None = None) -> CacheLayout:
    layout = build_cache_layout(root_manifest, cache_root)
    for path in (
        layout.root,
        layout.registry_packages,
        layout.git_checkouts,
        layout.git_sources,
        layout.temp,
        layout.locks,
    ):
        Path(path).mkdir(parents=True, exist_ok=True)
    return layout


def registry_cache_key(package: str, requirement: str, registry: str = "default") -> str:
    digest = _stable_hash(f"{registry}|{package}|{requirement}")
    return f"{_slug(package)}-{digest}"


def registry_package_path(
    layout: CacheLayout, package: str, requirement: str, registry: str = "default"
) -> Path:
    key = registry_cache_key(package, requirement, registry=registry)
    return Path(layout.registry_packages) / key


def git_cache_key(git_url: str, reference: str) -> str:
    return _stable_hash(f"{git_url}|{reference}")


def git_checkout_path(layout: CacheLayout, git_url: str, reference: str) -> Path:
    return Path(layout.git_checkouts) / git_cache_key(git_url, reference)


def git_source_path(layout: CacheLayout, git_url: str) -> Path:
    return Path(layout.git_sources) / _stable_hash(git_url)


def load_lockfile(lockfile_path: Path | str) -> tuple[dict[str, Any] | None, list[CacheDiagnostic]]:
    path = Path(lockfile_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return (
            None,
            [
                CacheDiagnostic(
                    code="CNXT5001",
                    path=str(path),
                    message=f"lockfile not found: {path}",
                )
            ],
        )
    except json.JSONDecodeError as exc:
        return (
            None,
            [
                CacheDiagnostic(
                    code="CNXT5002",
                    path=str(path),
                    message=f"invalid lockfile JSON: {exc}",
                )
            ],
        )

    if not isinstance(payload, dict):
        return (
            None,
            [
                CacheDiagnostic(
                    code="CNXT5003",
                    path=str(path),
                    message="lockfile root must be a JSON object",
                )
            ],
        )
    if payload.get("lockfile-version") != 1:
        return (
            None,
            [
                CacheDiagnostic(
                    code="CNXT5003",
                    path="lockfile-version",
                    message="unsupported lockfile-version; expected 1",
                )
            ],
        )
    return payload, []


def plan_cache_entries(lockfile: dict[str, Any], layout: CacheLayout) -> list[CacheEntry]:
    entries: list[CacheEntry] = []
    seen: set[tuple[str, str]] = set()

    packages = lockfile.get("packages", [])
    if not isinstance(packages, list):
        return entries

    for package in packages:
        if not isinstance(package, dict):
            continue
        dependencies = package.get("dependencies", [])
        if not isinstance(dependencies, list):
            continue
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                continue
            dep_name = dependency.get("name")
            source = dependency.get("source")
            if not isinstance(dep_name, str) or not isinstance(source, str):
                continue

            if source == "version":
                requirement = dependency.get("requirement")
                if not isinstance(requirement, str):
                    continue
                key = registry_cache_key(dep_name, requirement)
                dedupe_key = (source, key)
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                entries.append(
                    CacheEntry(
                        source="version",
                        package=dep_name,
                        key=key,
                        path=str(registry_package_path(layout, dep_name, requirement)),
                    )
                )
                continue

            if source == "git":
                git_url = dependency.get("git")
                if not isinstance(git_url, str):
                    continue
                reference = "HEAD"
                for ref_key in ("rev", "tag", "branch"):
                    value = dependency.get(ref_key)
                    if isinstance(value, str):
                        reference = value
                        break
                key = git_cache_key(git_url, reference)
                dedupe_key = (source, key)
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                entries.append(
                    CacheEntry(
                        source="git",
                        package=dep_name,
                        key=key,
                        path=str(git_checkout_path(layout, git_url, reference)),
                    )
                )

    entries.sort(key=lambda entry: (entry.source, entry.package, entry.key))
    return entries


def plan_cache(
    root_manifest: Path | str,
    lockfile_path: Path | str | None = None,
    cache_root: Path | str | None = None,
    initialize: bool = False,
) -> CachePlanResult:
    layout = (
        initialize_cache_layout(root_manifest, cache_root)
        if initialize
        else build_cache_layout(root_manifest, cache_root)
    )
    diagnostics: list[CacheDiagnostic] = []
    entries: list[CacheEntry] = []

    manifest_path = Path(root_manifest).resolve()
    lockfile = Path(lockfile_path).resolve() if lockfile_path else manifest_path.parent / "Cnxt.lock"
    if lockfile.exists():
        lock_payload, lock_diags = load_lockfile(lockfile)
        diagnostics.extend(lock_diags)
        if lock_payload is not None:
            entries = plan_cache_entries(lock_payload, layout)

    return CachePlanResult(layout=layout, entries=entries, diagnostics=diagnostics)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Plan local cNxt cache layout for downloaded packages"
    )
    parser.add_argument("manifest", type=Path, help="Path to root Cnxt.toml")
    parser.add_argument("--lockfile", type=Path, default=None, help="Path to Cnxt.lock")
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=None,
        help="Override cache root (default: <manifest-dir>/.cnxt/cache)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create cache directory structure on disk",
    )
    args = parser.parse_args(argv)

    result = plan_cache(args.manifest, args.lockfile, args.cache_root, initialize=args.init)
    payload = {
        "ok": result.ok,
        "layout": result.layout.to_dict(),
        "entries": [entry.to_dict() for entry in result.entries],
        "diagnostics": [diag.to_dict() for diag in result.diagnostics],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
