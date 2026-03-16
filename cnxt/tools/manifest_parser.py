#!/usr/bin/env python3
"""Schema validator for cNxt manifests (`Cnxt.toml`).

This parser validates against `cnxt/specs/cnxt-manifest-schema.md` and emits
structured diagnostics with stable IDs.
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


TOP_LEVEL_KEYS = {
    "manifest-version",
    "package",
    "dependencies",
    "dev-dependencies",
    "targets",
    "profile",
    "workspace",
}

PACKAGE_REQUIRED_KEYS = {"name", "version", "edition"}
PACKAGE_OPTIONAL_KEYS = {"description", "license", "repository", "type", "authors"}
PACKAGE_KEYS = PACKAGE_REQUIRED_KEYS | PACKAGE_OPTIONAL_KEYS

DEPENDENCY_KEYS = {
    "version",
    "path",
    "git",
    "rev",
    "tag",
    "branch",
    "optional",
    "features",
    "package",
}

TARGET_ROOT_KEYS = {"lib", "bin", "test"}
TARGET_ITEM_KEYS = {"name", "path", "required-features"}
PROFILE_KEYS = {"debug", "release"}
PROFILE_ITEM_KEYS = {"opt-level", "debug", "lto", "panic"}
WORKSPACE_KEYS = {"members", "exclude"}

NAME_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
SEMVER_REQ_RE = re.compile(r"^(?:\^|~|>=|<=|>|<)?\d+\.\d+\.\d+$")


class ManifestParseError(Exception):
    pass


def _strip_comment(line: str) -> str:
    in_string = False
    escaped = False
    for idx, char in enumerate(line):
        if char == "\\" and in_string and not escaped:
            escaped = True
            continue
        if char == '"' and not escaped:
            in_string = not in_string
        if char == "#" and not in_string:
            return line[:idx]
        escaped = False
    return line


def _split_top_level(value: str, sep: str = ",") -> list[str]:
    parts: list[str] = []
    start = 0
    depth_brace = 0
    depth_bracket = 0
    in_string = False
    escaped = False

    for idx, char in enumerate(value):
        if char == "\\" and in_string and not escaped:
            escaped = True
            continue
        if char == '"' and not escaped:
            in_string = not in_string
        elif not in_string:
            if char == "{":
                depth_brace += 1
            elif char == "}":
                depth_brace -= 1
            elif char == "[":
                depth_bracket += 1
            elif char == "]":
                depth_bracket -= 1
            elif char == sep and depth_brace == 0 and depth_bracket == 0:
                parts.append(value[start:idx].strip())
                start = idx + 1
        escaped = False

    parts.append(value[start:].strip())
    return [part for part in parts if part]


def _parse_toml_value(raw: str, line_no: int) -> Any:
    text = raw.strip()
    if not text:
        raise ManifestParseError(f"line {line_no}: missing value")

    if text.startswith('"') and text.endswith('"') and len(text) >= 2:
        return bytes(text[1:-1], "utf-8").decode("unicode_escape")

    if text in {"true", "false"}:
        return text == "true"

    if re.fullmatch(r"[+-]?\d+", text):
        return int(text)

    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_parse_toml_value(part, line_no) for part in _split_top_level(inner)]

    if text.startswith("{") and text.endswith("}"):
        inner = text[1:-1].strip()
        table: dict[str, Any] = {}
        if not inner:
            return table
        for item in _split_top_level(inner):
            if "=" not in item:
                raise ManifestParseError(f"line {line_no}: invalid inline table entry '{item}'")
            key, value = item.split("=", 1)
            table[key.strip()] = _parse_toml_value(value, line_no)
        return table

    raise ManifestParseError(f"line {line_no}: unsupported TOML value '{text}'")


def _ensure_table_path(root: dict[str, Any], path: list[str]) -> dict[str, Any]:
    table = root
    for key in path:
        existing = table.get(key)
        if existing is None:
            existing = {}
            table[key] = existing
        if not isinstance(existing, dict):
            raise ManifestParseError(f"invalid table path '{'.'.join(path)}'")
        table = existing
    return table


def parse_toml_minimal(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    current_table = root

    for idx, raw_line in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw_line).strip()
        if not line:
            continue

        if line.startswith("[[") and line.endswith("]]"):
            path = [segment.strip() for segment in line[2:-2].strip().split(".") if segment.strip()]
            if not path:
                raise ManifestParseError(f"line {idx}: empty array-of-table header")
            parent = _ensure_table_path(root, path[:-1])
            key = path[-1]
            existing = parent.get(key)
            if existing is None:
                existing = []
                parent[key] = existing
            if not isinstance(existing, list):
                raise ManifestParseError(f"line {idx}: '{'.'.join(path)}' must be an array")
            new_item: dict[str, Any] = {}
            existing.append(new_item)
            current_table = new_item
            continue

        if line.startswith("[") and line.endswith("]"):
            path = [segment.strip() for segment in line[1:-1].strip().split(".") if segment.strip()]
            if not path:
                raise ManifestParseError(f"line {idx}: empty table header")
            current_table = _ensure_table_path(root, path)
            continue

        if "=" not in line:
            raise ManifestParseError(f"line {idx}: expected key/value assignment")
        key, value = line.split("=", 1)
        current_table[key.strip()] = _parse_toml_value(value, idx)

    return root


@dataclass(frozen=True)
class Diagnostic:
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
class ManifestParseResult:
    manifest: dict[str, Any] | None
    diagnostics: list[Diagnostic]

    @property
    def ok(self) -> bool:
        return not self.diagnostics


class ManifestValidator:
    def __init__(self, manifest_dir: Path) -> None:
        self.manifest_dir = manifest_dir.resolve()
        self.diagnostics: list[Diagnostic] = []

    def add(self, code: str, path: str, message: str) -> None:
        self.diagnostics.append(Diagnostic(code=code, path=path, message=message))

    def validate(self, manifest: Any) -> list[Diagnostic]:
        if not isinstance(manifest, dict):
            self.add("CNXT1002", "<root>", "manifest root must be a TOML table")
            return self.diagnostics

        self._validate_top_level(manifest)
        self._validate_manifest_version(manifest)
        self._validate_package(manifest)
        self._validate_dependencies(manifest, "dependencies")
        self._validate_dependencies(manifest, "dev-dependencies")
        self._validate_targets(manifest)
        self._validate_profile(manifest)
        self._validate_workspace(manifest)
        return self.diagnostics

    def _validate_top_level(self, manifest: dict[str, Any]) -> None:
        for key in manifest:
            if key not in TOP_LEVEL_KEYS:
                self.add("CNXT1003", key, f"unknown top-level key '{key}'")

    def _validate_manifest_version(self, manifest: dict[str, Any]) -> None:
        if "manifest-version" not in manifest:
            self.add("CNXT1001", "manifest-version", "missing required key")
            return
        value = manifest["manifest-version"]
        if not isinstance(value, int):
            self.add("CNXT1002", "manifest-version", "manifest-version must be an integer")
            return
        if value != 1:
            self.add("CNXT1008", "manifest-version", "unsupported manifest-version; expected 1")

    def _validate_package(self, manifest: dict[str, Any]) -> None:
        raw = manifest.get("package")
        if raw is None:
            self.add("CNXT1001", "package", "missing required key")
            return
        if not isinstance(raw, dict):
            self.add("CNXT1002", "package", "package must be a table")
            return

        for key in raw:
            if key not in PACKAGE_KEYS:
                self.add("CNXT1003", f"package.{key}", f"unknown key '{key}'")
        for key in PACKAGE_REQUIRED_KEYS:
            if key not in raw:
                self.add("CNXT1001", f"package.{key}", "missing required key")

        name = raw.get("name")
        if name is not None:
            if not isinstance(name, str):
                self.add("CNXT1002", "package.name", "package.name must be a string")
            elif not NAME_RE.fullmatch(name):
                self.add(
                    "CNXT1004",
                    "package.name",
                    "package.name must match ^[a-z][a-z0-9_-]*$",
                )

        version = raw.get("version")
        if version is not None:
            if not isinstance(version, str):
                self.add("CNXT1002", "package.version", "package.version must be a string")
            elif not SEMVER_RE.fullmatch(version):
                self.add("CNXT1004", "package.version", "package.version must be MAJOR.MINOR.PATCH")

        edition = raw.get("edition")
        if edition is not None:
            if not isinstance(edition, str):
                self.add("CNXT1002", "package.edition", "package.edition must be a string")
            elif edition != "cnxt1":
                self.add("CNXT1008", "package.edition", "unsupported edition; expected 'cnxt1'")

        package_type = raw.get("type")
        if package_type is not None and package_type not in {"bin", "lib", "mixed"}:
            self.add("CNXT1004", "package.type", "package.type must be one of: bin, lib, mixed")

        authors = raw.get("authors")
        if authors is not None:
            if not isinstance(authors, list) or not all(isinstance(v, str) for v in authors):
                self.add("CNXT1002", "package.authors", "package.authors must be an array of strings")

    def _validate_dependencies(self, manifest: dict[str, Any], key: str) -> None:
        raw = manifest.get(key)
        if raw is None:
            return
        if not isinstance(raw, dict):
            self.add("CNXT1002", key, f"{key} must be a table")
            return

        for dep_name, dep_spec in raw.items():
            path = f"{key}.{dep_name}"
            if not NAME_RE.fullmatch(dep_name):
                self.add(
                    "CNXT1004",
                    path,
                    "dependency name must match ^[a-z][a-z0-9_-]*$",
                )

            if isinstance(dep_spec, str):
                if not SEMVER_REQ_RE.fullmatch(dep_spec):
                    self.add("CNXT1004", path, "invalid semantic version requirement")
                continue

            if not isinstance(dep_spec, dict):
                self.add(
                    "CNXT1002",
                    path,
                    "dependency spec must be a version string or an inline table",
                )
                continue

            for dep_key in dep_spec:
                if dep_key not in DEPENDENCY_KEYS:
                    self.add("CNXT1003", f"{path}.{dep_key}", f"unknown key '{dep_key}'")

            source_keys = [k for k in ("version", "path", "git") if k in dep_spec]
            if len(source_keys) != 1:
                self.add(
                    "CNXT1005",
                    path,
                    "dependency must specify exactly one source key: version, path, or git",
                )

            if "version" in dep_spec:
                value = dep_spec["version"]
                if not isinstance(value, str):
                    self.add("CNXT1002", f"{path}.version", "version must be a string")
                elif not SEMVER_REQ_RE.fullmatch(value):
                    self.add("CNXT1004", f"{path}.version", "invalid semantic version requirement")

            if "path" in dep_spec:
                self._validate_relative_path(dep_spec["path"], f"{path}.path")

            if "git" in dep_spec:
                git = dep_spec["git"]
                if not isinstance(git, str):
                    self.add("CNXT1002", f"{path}.git", "git must be a string URL")
                elif not (git.startswith("https://") or git.startswith("ssh://")):
                    self.add("CNXT1004", f"{path}.git", "git URL must use https:// or ssh://")

            refs = [k for k in ("rev", "tag", "branch") if k in dep_spec]
            if len(refs) > 1:
                self.add("CNXT1005", path, "at most one of rev/tag/branch can be set")
            for ref in refs:
                if not isinstance(dep_spec[ref], str):
                    self.add("CNXT1002", f"{path}.{ref}", f"{ref} must be a string")

            if "optional" in dep_spec:
                optional = dep_spec["optional"]
                if not isinstance(optional, bool):
                    self.add("CNXT1002", f"{path}.optional", "optional must be a bool")
                elif key == "dev-dependencies" and optional:
                    self.add(
                        "CNXT1005",
                        f"{path}.optional",
                        "optional=true is not allowed in dev-dependencies",
                    )

            if "features" in dep_spec:
                features = dep_spec["features"]
                if not isinstance(features, list) or not all(isinstance(v, str) for v in features):
                    self.add("CNXT1002", f"{path}.features", "features must be an array of strings")

            if "package" in dep_spec and not isinstance(dep_spec["package"], str):
                self.add("CNXT1002", f"{path}.package", "package must be a string")

    def _validate_targets(self, manifest: dict[str, Any]) -> None:
        raw = manifest.get("targets")
        if raw is None:
            return
        if not isinstance(raw, dict):
            self.add("CNXT1002", "targets", "targets must be a table")
            return

        for key in raw:
            if key not in TARGET_ROOT_KEYS:
                self.add("CNXT1003", f"targets.{key}", f"unknown key '{key}'")

        lib = raw.get("lib")
        if lib is not None:
            self._validate_target_item(lib, "targets.lib", require_name=False, seen_names=set())

        for kind in ("bin", "test"):
            value = raw.get(kind)
            if value is None:
                continue
            if not isinstance(value, list):
                self.add("CNXT1002", f"targets.{kind}", f"targets.{kind} must be an array of tables")
                continue
            seen_names: set[str] = set()
            for idx, item in enumerate(value):
                self._validate_target_item(
                    item,
                    f"targets.{kind}[{idx}]",
                    require_name=True,
                    seen_names=seen_names,
                )

    def _validate_target_item(
        self, item: Any, path: str, require_name: bool, seen_names: set[str]
    ) -> None:
        if not isinstance(item, dict):
            self.add("CNXT1002", path, "target entry must be a table")
            return
        for key in item:
            if key not in TARGET_ITEM_KEYS:
                self.add("CNXT1003", f"{path}.{key}", f"unknown key '{key}'")

        if "path" not in item:
            self.add("CNXT1001", f"{path}.path", "missing required key")
        else:
            self._validate_relative_path(item["path"], f"{path}.path", require_cnxt_ext=True)

        if require_name:
            if "name" not in item:
                self.add("CNXT1001", f"{path}.name", "missing required key")
            else:
                name = item["name"]
                if not isinstance(name, str):
                    self.add("CNXT1002", f"{path}.name", "name must be a string")
                elif name in seen_names:
                    self.add("CNXT1007", f"{path}.name", f"duplicate target name '{name}'")
                else:
                    seen_names.add(name)

        if "required-features" in item:
            features = item["required-features"]
            if not isinstance(features, list) or not all(isinstance(v, str) for v in features):
                self.add(
                    "CNXT1002",
                    f"{path}.required-features",
                    "required-features must be an array of strings",
                )

    def _validate_profile(self, manifest: dict[str, Any]) -> None:
        raw = manifest.get("profile")
        if raw is None:
            return
        if not isinstance(raw, dict):
            self.add("CNXT1002", "profile", "profile must be a table")
            return
        for profile_name, profile_data in raw.items():
            path = f"profile.{profile_name}"
            if profile_name not in PROFILE_KEYS:
                self.add("CNXT1003", path, f"unknown profile '{profile_name}'")
                continue
            if not isinstance(profile_data, dict):
                self.add("CNXT1002", path, "profile entry must be a table")
                continue
            for key, value in profile_data.items():
                key_path = f"{path}.{key}"
                if key not in PROFILE_ITEM_KEYS:
                    self.add("CNXT1003", key_path, f"unknown key '{key}'")
                    continue
                if key == "opt-level":
                    if not isinstance(value, int):
                        self.add("CNXT1002", key_path, "opt-level must be an integer")
                    elif value < 0 or value > 3:
                        self.add("CNXT1004", key_path, "opt-level must be in range 0..3")
                elif key in {"debug", "lto"} and not isinstance(value, bool):
                    self.add("CNXT1002", key_path, f"{key} must be a bool")
                elif key == "panic":
                    if not isinstance(value, str):
                        self.add("CNXT1002", key_path, "panic must be a string")
                    elif value not in {"abort", "unwind"}:
                        self.add("CNXT1004", key_path, "panic must be 'abort' or 'unwind'")

    def _validate_workspace(self, manifest: dict[str, Any]) -> None:
        raw = manifest.get("workspace")
        if raw is None:
            return
        if not isinstance(raw, dict):
            self.add("CNXT1002", "workspace", "workspace must be a table")
            return
        for key in raw:
            if key not in WORKSPACE_KEYS:
                self.add("CNXT1003", f"workspace.{key}", f"unknown key '{key}'")

        if "members" not in raw:
            self.add("CNXT1001", "workspace.members", "missing required key")
        elif not isinstance(raw["members"], list) or not all(
            isinstance(v, str) for v in raw["members"]
        ):
            self.add("CNXT1002", "workspace.members", "members must be an array of strings")
        else:
            for idx, value in enumerate(raw["members"]):
                self._validate_relative_path(value, f"workspace.members[{idx}]")

        if "exclude" in raw:
            exclude = raw["exclude"]
            if not isinstance(exclude, list) or not all(isinstance(v, str) for v in exclude):
                self.add("CNXT1002", "workspace.exclude", "exclude must be an array of strings")
            else:
                for idx, value in enumerate(exclude):
                    self._validate_relative_path(value, f"workspace.exclude[{idx}]")

    def _validate_relative_path(
        self, value: Any, path: str, require_cnxt_ext: bool = False
    ) -> None:
        if not isinstance(value, str):
            self.add("CNXT1002", path, "path must be a string")
            return

        candidate = Path(value)
        if candidate.is_absolute():
            self.add("CNXT1006", path, "path must be relative")
            return

        resolved = (self.manifest_dir / candidate).resolve()
        try:
            resolved.relative_to(self.manifest_dir)
        except ValueError:
            self.add("CNXT1006", path, "path must not escape manifest directory")
            return

        if require_cnxt_ext and candidate.suffix not in {".cn", ".cnxt"}:
            self.add("CNXT1004", path, "path must end with .cn or .cnxt")


def parse_manifest_file(manifest_path: Path | str) -> ManifestParseResult:
    path = Path(manifest_path)
    try:
        if tomllib is not None:
            with path.open("rb") as handle:
                manifest_data = tomllib.load(handle)
        else:
            manifest_data = parse_toml_minimal(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ManifestParseResult(
            manifest=None,
            diagnostics=[Diagnostic("CNXT1006", "<root>", f"manifest not found: {path}")],
        )
    except Exception as exc:  # TOML decode / minimal parser errors
        if tomllib is not None and isinstance(exc, tomllib.TOMLDecodeError):
            message = f"TOML parse error: {exc}"
        elif isinstance(exc, ManifestParseError):
            message = f"TOML parse error: {exc}"
        else:
            raise
        return ManifestParseResult(
            manifest=None,
            diagnostics=[Diagnostic("CNXT1002", "<root>", message)],
        )

    validator = ManifestValidator(path.parent)
    diagnostics = validator.validate(manifest_data)
    return ManifestParseResult(manifest=manifest_data, diagnostics=diagnostics)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a cNxt Cnxt.toml manifest")
    parser.add_argument("manifest", type=Path, help="Path to Cnxt.toml")
    args = parser.parse_args(argv)

    result = parse_manifest_file(args.manifest)
    payload = {
        "ok": result.ok,
        "manifest": result.manifest if result.ok else None,
        "diagnostics": [diag.to_dict() for diag in result.diagnostics],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
