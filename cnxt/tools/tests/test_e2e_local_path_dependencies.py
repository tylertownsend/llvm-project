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
echo "e2e-test"
exit 0
EOF
else
  cat > "${out}" <<'EOF'
#!/usr/bin/env bash
echo "e2e-run"
exit 0
EOF
fi
chmod +x "${out}"
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


class LocalPathE2ETests(unittest.TestCase):
    def test_local_path_dependency_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            workspace_manifest = tmp / "project" / "Cnxt.toml"
            app_manifest = tmp / "project" / "app" / "Cnxt.toml"
            util_manifest = tmp / "project" / "app" / "vendor" / "util" / "Cnxt.toml"
            app_main = tmp / "project" / "app" / "src" / "main.cn"
            app_test = tmp / "project" / "app" / "tests" / "smoke.cn"
            util_lib = tmp / "project" / "app" / "vendor" / "util" / "src" / "lib.cn"
            compiler = tmp / "fake-clang.sh"

            write_manifest(
                workspace_manifest,
                """
manifest-version = 1

[package]
name = "workspace"
version = "0.1.0"
edition = "cnxt1"

[workspace]
members = ["app", "app/vendor/util"]
""",
            )
            write_manifest(
                app_manifest,
                """
manifest-version = 1

[package]
name = "app"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
util = { path = "vendor/util" }

[targets]
bin = [{ name = "app", path = "src/main.cn" }]
test = [{ name = "smoke", path = "tests/smoke.cn" }]
""",
            )
            write_manifest(
                util_manifest,
                """
manifest-version = 1

[package]
name = "util"
version = "0.2.0"
edition = "cnxt1"
""",
            )
            app_main.parent.mkdir(parents=True, exist_ok=True)
            app_test.parent.mkdir(parents=True, exist_ok=True)
            util_lib.parent.mkdir(parents=True, exist_ok=True)
            app_main.write_text("fn main() {}\n", encoding="utf-8")
            app_test.write_text("fn main() {}\n", encoding="utf-8")
            util_lib.write_text("fn helper() {}\n", encoding="utf-8")
            write_mock_compiler(compiler)

            build_result = cnxt_build.run_build(
                app_manifest,
                skip_fetch=False,
                dry_run=False,
                compiler=str(compiler),
            )
            self.assertTrue(build_result.ok)

            lockfile_path = app_manifest.parent / "Cnxt.lock"
            lock_payload = json.loads(lockfile_path.read_text(encoding="utf-8"))
            package_names = {pkg["name"] for pkg in lock_payload["packages"]}
            self.assertEqual({"app", "util"}, package_names)

            run_result = cnxt_run.run_package(
                app_manifest,
                skip_fetch=False,
                compiler=str(compiler),
            )
            self.assertTrue(run_result.ok)
            self.assertIn("e2e-run", run_result.stdout)

            test_result = cnxt_test.run_tests(
                app_manifest,
                skip_fetch=False,
                compiler=str(compiler),
            )
            self.assertTrue(test_result.ok)
            self.assertEqual(1, len(test_result.executions))
            self.assertEqual("passed", test_result.executions[0].status)

    def test_directory_input_with_local_path_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            app_manifest = tmp / "project" / "app" / "Cnxt.toml"
            util_manifest = tmp / "project" / "app" / "vendor" / "util" / "Cnxt.toml"
            app_main = tmp / "project" / "app" / "src" / "main.cn"

            write_manifest(
                app_manifest,
                """
manifest-version = 1

[package]
name = "app"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
util = { path = "vendor/util" }
""",
            )
            write_manifest(
                util_manifest,
                """
manifest-version = 1

[package]
name = "util"
version = "0.2.0"
edition = "cnxt1"
""",
            )
            app_main.parent.mkdir(parents=True, exist_ok=True)
            app_main.write_text("fn main() {}\n", encoding="utf-8")

            result = cnxt_build.run_build(app_manifest.parent, dry_run=True, skip_fetch=False)
            self.assertTrue(result.ok)
            self.assertTrue((app_manifest.parent / "Cnxt.lock").exists())


if __name__ == "__main__":
    unittest.main()
