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
cnxt_run = load_module("cnxt_run", "cnxt_run.py")
cnxt_test = load_module("cnxt_test", "cnxt_test.py")


def write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def diag_codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


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
if [[ "${out}" == *.test ]]; then
  cat > "${out}" <<'EOF'
#!/usr/bin/env bash
echo "registry-test"
exit 0
EOF
else
  cat > "${out}" <<'EOF'
#!/usr/bin/env bash
echo "registry-run"
exit 0
EOF
fi
chmod +x "${out}"
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def write_registry(registry_root: Path, versions: list[tuple[str, str]]) -> None:
    (registry_root / "index").mkdir(parents=True, exist_ok=True)
    for version, payload_text in versions:
        artifact = registry_root / "artifacts" / f"json-{version}"
        artifact.mkdir(parents=True, exist_ok=True)
        (artifact / "payload.txt").write_text(payload_text, encoding="utf-8")
    (registry_root / "index" / "json.json").write_text(
        json.dumps(
            {
                "versions": [
                    {"version": version, "source": f"artifacts/json-{version}"}
                    for version, _ in versions
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )


class RegistryE2ETests(unittest.TestCase):
    def test_registry_dependency_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "project" / "Cnxt.toml"
            source = tmp / "project" / "src" / "main.cn"
            test_src = tmp / "project" / "tests" / "smoke.cn"
            compiler = tmp / "fake-clang.sh"
            registry_root = tmp / "registry"

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

[targets]
bin = [{ name = "app", path = "src/main.cn" }]
test = [{ name = "smoke", path = "tests/smoke.cn" }]
""",
            )
            source.parent.mkdir(parents=True, exist_ok=True)
            test_src.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("fn main() {}\n", encoding="utf-8")
            test_src.write_text("fn main() {}\n", encoding="utf-8")
            write_mock_compiler(compiler)
            write_registry(
                registry_root,
                [("1.0.0", "json 1.0.0\n"), ("1.5.0", "json 1.5.0\n")],
            )

            build_result = cnxt_build.run_build(
                manifest,
                skip_fetch=False,
                dry_run=False,
                compiler=str(compiler),
                registry=str(registry_root),
            )
            self.assertTrue(build_result.ok)

            cache_meta_files = list(
                (manifest.parent / ".cnxt" / "cache" / "registry" / "packages").glob("*/meta.json")
            )
            self.assertTrue(cache_meta_files)
            resolved = json.loads(cache_meta_files[0].read_text(encoding="utf-8"))
            self.assertEqual("1.5.0", resolved["resolved-version"])

            run_result = cnxt_run.run_package(
                manifest,
                skip_fetch=False,
                compiler=str(compiler),
                registry=str(registry_root),
            )
            self.assertTrue(run_result.ok)
            self.assertIn("registry-run", run_result.stdout)

            test_result = cnxt_test.run_tests(
                manifest,
                skip_fetch=False,
                compiler=str(compiler),
                registry=str(registry_root),
            )
            self.assertTrue(test_result.ok)
            self.assertEqual(1, len(test_result.executions))
            self.assertEqual("passed", test_result.executions[0].status)

    def test_unsatisfied_registry_requirement_fails_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "project" / "Cnxt.toml"
            source = tmp / "project" / "src" / "main.cn"
            compiler = tmp / "fake-clang.sh"
            registry_root = tmp / "registry"

            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "app"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
json = ">=3.0.0"
""",
            )
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("fn main() {}\n", encoding="utf-8")
            write_mock_compiler(compiler)
            write_registry(registry_root, [("1.0.0", "json 1.0.0\n"), ("1.5.0", "json 1.5.0\n")])

            result = cnxt_build.run_build(
                manifest,
                skip_fetch=False,
                dry_run=False,
                compiler=str(compiler),
                registry=str(registry_root),
            )
            self.assertFalse(result.ok)
            self.assertIn("CNXT6004", diag_codes(result))


if __name__ == "__main__":
    unittest.main()
