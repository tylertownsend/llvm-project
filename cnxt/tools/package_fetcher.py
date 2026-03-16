#!/usr/bin/env python3
"""Package fetcher for cNxt lockfiles (registry and git sources)."""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_TOOLS_DIR = Path(__file__).resolve().parent
_cache_module = _load_module("cnxt_cache_layout", _TOOLS_DIR / "cache_layout.py")
_solver_module = _load_module("cnxt_version_solver", _TOOLS_DIR / "version_solver.py")
compute_cache_root = _cache_module.compute_cache_root
initialize_cache_layout = _cache_module.initialize_cache_layout
load_lockfile = _cache_module.load_lockfile
registry_package_path = _cache_module.registry_package_path
git_checkout_path = _cache_module.git_checkout_path
git_source_path = _cache_module.git_source_path
parse_requirement_to_range = _solver_module.parse_requirement_to_range
Version = _solver_module.Version


@dataclass(frozen=True)
class FetchDiagnostic:
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
class FetchRecord:
    package: str
    source: str
    detail: str
    path: str
    status: str

    def to_dict(self) -> dict[str, str]:
        return {
            "package": self.package,
            "source": self.source,
            "detail": self.detail,
            "path": self.path,
            "status": self.status,
        }


@dataclass(frozen=True)
class FetchResult:
    cache_root: str
    records: list[FetchRecord]
    diagnostics: list[FetchDiagnostic]

    @property
    def ok(self) -> bool:
        return not self.diagnostics


def _is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "file"}


def _read_json_source(source: str | Path) -> dict[str, Any]:
    if isinstance(source, Path):
        return json.loads(source.read_text(encoding="utf-8"))
    if _is_url(source):
        with urlopen(source) as response:  # nosec B310 - tool intentionally fetches URLs
            return json.loads(response.read().decode("utf-8"))
    return json.loads(Path(source).read_text(encoding="utf-8"))


def _resolve_registry_index_path(registry: str | Path, package: str) -> str | Path:
    if isinstance(registry, Path):
        return registry / "index" / f"{package}.json"
    if _is_url(registry):
        return registry.rstrip("/") + f"/index/{package}.json"
    return Path(registry) / "index" / f"{package}.json"


def _resolve_registry_source(registry: str | Path, source: str) -> str | Path:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https", "file"}:
        return source
    if isinstance(registry, Path):
        return (registry / source).resolve()
    if _is_url(str(registry)):
        return str(registry).rstrip("/") + "/" + source.lstrip("/")
    return (Path(str(registry)) / source).resolve()


def _load_registry_package_versions(
    registry: str | Path, package: str
) -> tuple[list[dict[str, Any]] | None, list[FetchDiagnostic]]:
    index_source = _resolve_registry_index_path(registry, package)
    try:
        payload = _read_json_source(index_source)
    except FileNotFoundError:
        return (
            None,
            [
                FetchDiagnostic(
                    code="CNXT6003",
                    path=f"registry.index.{package}",
                    message=f"registry index not found for package '{package}'",
                )
            ],
        )
    except Exception as exc:
        return (
            None,
            [
                FetchDiagnostic(
                    code="CNXT6003",
                    path=f"registry.index.{package}",
                    message=f"failed to read registry index for '{package}': {exc}",
                )
            ],
        )

    versions = payload.get("versions")
    if not isinstance(versions, list):
        return (
            None,
            [
                FetchDiagnostic(
                    code="CNXT6003",
                    path=f"registry.index.{package}",
                    message=f"registry index for '{package}' is missing a versions array",
                )
            ],
        )
    return versions, []


def _select_registry_version(
    versions: list[dict[str, Any]], requirement: str
) -> tuple[dict[str, Any] | None, list[FetchDiagnostic]]:
    req_range = parse_requirement_to_range(requirement)
    if req_range is None:
        return (
            None,
            [
                FetchDiagnostic(
                    code="CNXT6004",
                    path=f"requirement.{requirement}",
                    message=f"unsupported version requirement '{requirement}'",
                )
            ],
        )

    candidates: list[tuple[Any, dict[str, Any]]] = []
    for version_entry in versions:
        if not isinstance(version_entry, dict):
            continue
        version = version_entry.get("version")
        source = version_entry.get("source")
        if not isinstance(version, str) or not isinstance(source, str):
            continue
        parsed = Version.parse(version)
        if parsed is None:
            continue
        if req_range.contains(parsed):
            candidates.append((parsed, version_entry))

    if not candidates:
        return (
            None,
            [
                FetchDiagnostic(
                    code="CNXT6004",
                    path=f"requirement.{requirement}",
                    message=f"no registry versions satisfy requirement '{requirement}'",
                )
            ],
        )

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1], []


def _copy_source_into_dir(source: str | Path, destination: Path) -> None:
    content_dir = destination / "content"
    content_dir.mkdir(parents=True, exist_ok=True)

    if isinstance(source, Path):
        resolved = source.resolve()
        if resolved.is_dir():
            shutil.copytree(resolved, content_dir, dirs_exist_ok=True)
            return
        if resolved.is_file():
            shutil.copy2(resolved, content_dir / resolved.name)
            return
        raise FileNotFoundError(f"source path does not exist: {resolved}")

    parsed = urlparse(source)
    if parsed.scheme in {"http", "https", "file"}:
        with urlopen(source) as response:  # nosec B310 - tool intentionally fetches URLs
            data = response.read()
        filename = Path(parsed.path).name or "download"
        (content_dir / filename).write_bytes(data)
        return

    resolved = Path(source).resolve()
    if resolved.is_dir():
        shutil.copytree(resolved, content_dir, dirs_exist_ok=True)
        return
    if resolved.is_file():
        shutil.copy2(resolved, content_dir / resolved.name)
        return
    raise FileNotFoundError(f"source path does not exist: {resolved}")


def _run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=True, capture_output=True, text=True)


def _fetch_git_checkout(git_url: str, reference: str, checkout_path: Path, source_path: Path) -> str:
    source_parent = source_path.parent
    source_parent.mkdir(parents=True, exist_ok=True)
    checkout_path.parent.mkdir(parents=True, exist_ok=True)

    if not source_path.exists():
        _run_git(["git", "clone", "--mirror", git_url, str(source_path)])
    else:
        _run_git(["git", "-C", str(source_path), "fetch", "--all", "--prune"])

    if checkout_path.exists():
        _run_git(["git", "-C", str(checkout_path), "fetch", "--all", "--prune"])
        _run_git(["git", "-C", str(checkout_path), "checkout", reference])
        return "cached"

    _run_git(["git", "clone", str(source_path), str(checkout_path)])
    _run_git(["git", "-C", str(checkout_path), "checkout", reference])
    return "fetched"


def _iter_unique_lockfile_dependencies(lock_payload: dict[str, Any]) -> list[dict[str, str]]:
    seen: set[tuple[str, str, str]] = set()
    collected: list[dict[str, str]] = []

    packages = lock_payload.get("packages", [])
    if not isinstance(packages, list):
        return collected

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
            dep_source = dependency.get("source")
            if not isinstance(dep_name, str) or not isinstance(dep_source, str):
                continue
            if dep_source == "version":
                requirement = dependency.get("requirement")
                if not isinstance(requirement, str):
                    continue
                key = (dep_source, dep_name, requirement)
                if key in seen:
                    continue
                seen.add(key)
                collected.append(
                    {"source": dep_source, "name": dep_name, "requirement": requirement}
                )
            elif dep_source == "git":
                git_url = dependency.get("git")
                if not isinstance(git_url, str):
                    continue
                reference = "HEAD"
                for ref_key in ("rev", "tag", "branch"):
                    value = dependency.get(ref_key)
                    if isinstance(value, str):
                        reference = value
                        break
                key = (dep_source, dep_name, f"{git_url}@{reference}")
                if key in seen:
                    continue
                seen.add(key)
                collected.append(
                    {
                        "source": dep_source,
                        "name": dep_name,
                        "git": git_url,
                        "reference": reference,
                    }
                )

    collected.sort(
        key=lambda item: (
            item.get("source", ""),
            item.get("name", ""),
            item.get("requirement", item.get("reference", "")),
        )
    )
    return collected


def fetch_packages(
    root_manifest: Path | str,
    lockfile_path: Path | str | None = None,
    registry: Path | str | None = None,
    cache_root: Path | str | None = None,
) -> FetchResult:
    manifest_path = Path(root_manifest).resolve()
    cache_layout = initialize_cache_layout(manifest_path, cache_root)
    diagnostics: list[FetchDiagnostic] = []
    records: list[FetchRecord] = []

    lock_path = Path(lockfile_path).resolve() if lockfile_path else manifest_path.parent / "Cnxt.lock"
    lock_payload, lock_diags = load_lockfile(lock_path)
    diagnostics.extend(
        FetchDiagnostic(code=diag.code, message=diag.message, path=diag.path)
        for diag in lock_diags
    )
    if lock_payload is None:
        return FetchResult(cache_root=cache_layout.root, records=records, diagnostics=diagnostics)

    registry_root: Path | str = registry if registry is not None else manifest_path.parent / "registry"
    dependencies = _iter_unique_lockfile_dependencies(lock_payload)
    for dependency in dependencies:
        if dependency["source"] == "version":
            package_name = dependency["name"]
            requirement = dependency["requirement"]
            versions, version_diags = _load_registry_package_versions(registry_root, package_name)
            diagnostics.extend(version_diags)
            if versions is None:
                continue
            selected, select_diags = _select_registry_version(versions, requirement)
            diagnostics.extend(select_diags)
            if selected is None:
                continue
            version = selected.get("version")
            source = selected.get("source")
            if not isinstance(version, str) or not isinstance(source, str):
                diagnostics.append(
                    FetchDiagnostic(
                        code="CNXT6003",
                        path=f"registry.index.{package_name}",
                        message=f"registry version entry missing version/source for '{package_name}'",
                    )
                )
                continue

            destination = registry_package_path(cache_layout, package_name, requirement)
            status = "cached" if destination.exists() else "fetched"
            if not destination.exists():
                destination.mkdir(parents=True, exist_ok=True)
                meta = {
                    "package": package_name,
                    "requirement": requirement,
                    "resolved-version": version,
                    "source": source,
                }
                (destination / "meta.json").write_text(
                    json.dumps(meta, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                resolved_source = _resolve_registry_source(registry_root, source)
                try:
                    _copy_source_into_dir(resolved_source, destination)
                except Exception as exc:
                    diagnostics.append(
                        FetchDiagnostic(
                            code="CNXT6003",
                            path=f"registry.fetch.{package_name}",
                            message=f"failed to fetch registry source for '{package_name}': {exc}",
                        )
                    )
                    continue

            records.append(
                FetchRecord(
                    package=package_name,
                    source="version",
                    detail=f"{requirement} -> {version}",
                    path=str(destination),
                    status=status,
                )
            )
            continue

        if dependency["source"] == "git":
            package_name = dependency["name"]
            git_url = dependency["git"]
            reference = dependency["reference"]
            checkout = git_checkout_path(cache_layout, git_url, reference)
            source = git_source_path(cache_layout, git_url)
            try:
                status = _fetch_git_checkout(git_url, reference, checkout, source)
            except Exception as exc:
                diagnostics.append(
                    FetchDiagnostic(
                        code="CNXT6005",
                        path=f"git.fetch.{package_name}",
                        message=f"failed to fetch git dependency '{package_name}': {exc}",
                    )
                )
                continue

            records.append(
                FetchRecord(
                    package=package_name,
                    source="git",
                    detail=f"{git_url}@{reference}",
                    path=str(checkout),
                    status=status,
                )
            )

    return FetchResult(cache_root=cache_layout.root, records=records, diagnostics=diagnostics)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch cNxt lockfile dependencies into local cache (registry + git)"
    )
    parser.add_argument("manifest", type=Path, help="Path to root Cnxt.toml")
    parser.add_argument("--lockfile", type=Path, default=None, help="Path to Cnxt.lock")
    parser.add_argument(
        "--registry",
        type=str,
        default=None,
        help=(
            "Registry root path/URL containing index/<package>.json. "
            "Defaults to <manifest-dir>/registry"
        ),
    )
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=None,
        help="Override cache root (default: <manifest-dir>/.cnxt/cache)",
    )
    args = parser.parse_args(argv)

    result = fetch_packages(args.manifest, args.lockfile, args.registry, args.cache_root)
    payload = {
        "ok": result.ok,
        "cache_root": result.cache_root,
        "records": [record.to_dict() for record in result.records],
        "diagnostics": [diag.to_dict() for diag in result.diagnostics],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
