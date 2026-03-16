from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


def load_module(name: str, relative_path: str):
    module_path = Path(__file__).resolve().parents[1] / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cnxt_build = load_module("cnxt_build", "cnxt_build.py")


def write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_mock_compiler(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
out=""
is_compile=0
while [[ $# -gt 0 ]]; do
  if [[ "$1" == "-c" ]]; then
    is_compile=1
  fi
  if [[ "$1" == "-o" ]]; then
    out="$2"
    shift 2
    continue
  fi
  shift
done
if [[ -z "${out}" ]]; then
  echo "missing -o output" >&2
  exit 1
fi
mkdir -p "$(dirname "${out}")"
if [[ "${is_compile}" -eq 1 ]]; then
  echo "obj" > "${out}"
  exit 0
fi
cat > "${out}" <<'EOF'
#!/usr/bin/env bash
echo "lock-replay"
exit 0
EOF
chmod +x "${out}"
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def write_registry_versions(registry_root: Path, versions: list[str]) -> None:
    (registry_root / "index").mkdir(parents=True, exist_ok=True)
    version_entries = []
    for version in versions:
        artifact = registry_root / "artifacts" / f"json-{version}"
        artifact.mkdir(parents=True, exist_ok=True)
        (artifact / "payload.txt").write_text(f"json {version}\n", encoding="utf-8")
        version_entries.append({"version": version, "source": f"artifacts/json-{version}"})
    (registry_root / "index" / "json.json").write_text(
        json.dumps({"versions": version_entries}, indent=2),
        encoding="utf-8",
    )


def diag_codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


class LockfileReplayE2ETests(unittest.TestCase):
    def test_locked_build_replays_pinned_registry_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "project" / "Cnxt.toml"
            source = tmp / "project" / "src" / "main.cn"
            registry_root = tmp / "registry"
            compiler = tmp / "fake-clang.sh"

            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "app"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
json = "^1.0.0"
""",
            )
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("fn main() {}\n", encoding="utf-8")
            write_mock_compiler(compiler)
            write_registry_versions(registry_root, ["1.0.0", "1.5.0"])

            first = cnxt_build.run_build(
                manifest,
                skip_fetch=False,
                dry_run=False,
                compiler=str(compiler),
                registry=str(registry_root),
            )
            self.assertTrue(first.ok)

            lockfile_path = manifest.parent / "Cnxt.lock"
            lock_before = lockfile_path.read_text(encoding="utf-8")
            payload = json.loads(lock_before)
            app_pkg = next(pkg for pkg in payload["packages"] if pkg["name"] == "app")
            dep = next(dep for dep in app_pkg["dependencies"] if dep["name"] == "json")
            self.assertEqual("1.5.0", dep["resolved-version"])

            write_registry_versions(registry_root, ["1.0.0", "1.5.0", "1.9.0"])
            second = cnxt_build.run_build(
                manifest,
                skip_fetch=False,
                dry_run=False,
                locked=True,
                compiler=str(compiler),
                registry=str(registry_root),
            )
            self.assertTrue(second.ok)
            lock_after = lockfile_path.read_text(encoding="utf-8")
            self.assertEqual(lock_before, lock_after)

    def test_locked_build_requires_existing_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "project" / "Cnxt.toml"
            source = tmp / "project" / "src" / "main.cn"
            compiler = tmp / "fake-clang.sh"

            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "app"
version = "0.1.0"
edition = "cnxt1"
""",
            )
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("fn main() {}\n", encoding="utf-8")
            write_mock_compiler(compiler)

            result = cnxt_build.run_build(
                manifest,
                skip_fetch=True,
                dry_run=True,
                locked=True,
                compiler=str(compiler),
            )
            self.assertFalse(result.ok)
            self.assertIn("CNXT7005", diag_codes(result))


if __name__ == "__main__":
    unittest.main()
