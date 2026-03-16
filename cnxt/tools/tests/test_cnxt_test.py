from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "cnxt_test.py"
SPEC = importlib.util.spec_from_file_location("cnxt_test", MODULE_PATH)
assert SPEC and SPEC.loader
cnxt_test = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cnxt_test
SPEC.loader.exec_module(cnxt_test)


def write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def diag_codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


def write_test_compiler(path: Path) -> None:
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
if [[ "${out}" == *"fail.test" ]]; then
  cat > "${out}" <<'EOF'
#!/usr/bin/env bash
echo "fail"
exit 1
EOF
else
  cat > "${out}" <<'EOF'
#!/usr/bin/env bash
echo "pass"
exit 0
EOF
fi
chmod +x "${out}"
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


class CnxtTestTests(unittest.TestCase):
    def test_runs_test_targets_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            source = tmp / "root" / "tests" / "ok.cn"
            compiler = tmp / "fake-clang.sh"

            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "demo"
version = "0.1.0"
edition = "cnxt1"

[targets]
test = [{ name = "ok", path = "tests/ok.cn" }]
""",
            )
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("fn main() {}\n", encoding="utf-8")
            write_test_compiler(compiler)

            result = cnxt_test.run_tests(
                manifest,
                skip_fetch=True,
                compiler=str(compiler),
            )
            self.assertTrue(result.ok)
            self.assertEqual(1, len(result.executions))
            self.assertEqual("passed", result.executions[0].status)

    def test_reports_failing_test_binary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            source_ok = tmp / "root" / "tests" / "ok.cn"
            source_fail = tmp / "root" / "tests" / "fail.cn"
            compiler = tmp / "fake-clang.sh"

            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "demo"
version = "0.1.0"
edition = "cnxt1"

[targets]
test = [{ name = "ok", path = "tests/ok.cn" }, { name = "fail", path = "tests/fail.cn" }]
""",
            )
            source_ok.parent.mkdir(parents=True, exist_ok=True)
            source_ok.write_text("fn main() {}\n", encoding="utf-8")
            source_fail.write_text("fn main() {}\n", encoding="utf-8")
            write_test_compiler(compiler)

            result = cnxt_test.run_tests(
                manifest,
                skip_fetch=True,
                compiler=str(compiler),
            )
            self.assertFalse(result.ok)
            self.assertIn("CNXT7203", diag_codes(result))
            statuses = {execution.name: execution.status for execution in result.executions}
            self.assertEqual("passed", statuses["ok"])
            self.assertEqual("failed", statuses["fail"])

    def test_no_tests_emits_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            source = tmp / "root" / "src" / "main.cn"
            compiler = tmp / "fake-clang.sh"

            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "demo"
version = "0.1.0"
edition = "cnxt1"
""",
            )
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("fn main() {}\n", encoding="utf-8")
            write_test_compiler(compiler)

            result = cnxt_test.run_tests(
                manifest,
                skip_fetch=True,
                compiler=str(compiler),
            )
            self.assertFalse(result.ok)
            self.assertIn("CNXT7201", diag_codes(result))


if __name__ == "__main__":
    unittest.main()
