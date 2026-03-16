from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "cnxt_run.py"
SPEC = importlib.util.spec_from_file_location("cnxt_run", MODULE_PATH)
assert SPEC and SPEC.loader
cnxt_run = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cnxt_run
SPEC.loader.exec_module(cnxt_run)


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
cat > "${out}" <<'EOF'
#!/usr/bin/env bash
echo "hello-run $*"
EOF
chmod +x "${out}"
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


class CnxtRunTests(unittest.TestCase):
    def test_run_builds_and_executes_binary(self) -> None:
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
name = "hello"
version = "0.1.0"
edition = "cnxt1"
""",
            )
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("fn main() {}\n", encoding="utf-8")
            write_mock_compiler(compiler)

            result = cnxt_run.run_package(
                manifest,
                run_args=["one", "two"],
                skip_fetch=True,
                compiler=str(compiler),
            )
            self.assertTrue(result.ok)
            self.assertEqual(0, result.exit_code)
            self.assertIn("hello-run one two", result.stdout.strip())

    def test_skip_build_reports_missing_binary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "hello"
version = "0.1.0"
edition = "cnxt1"
""",
            )

            result = cnxt_run.run_package(manifest, skip_build=True)
            self.assertFalse(result.ok)
            self.assertIn("CNXT7102", diag_codes(result))

    def test_named_binary_must_exist_in_build_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            source = tmp / "root" / "src" / "tool.cn"
            compiler = tmp / "fake-clang.sh"

            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "hello"
version = "0.1.0"
edition = "cnxt1"

[targets]
bin = [{ name = "tool", path = "src/tool.cn" }]
""",
            )
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("fn main() {}\n", encoding="utf-8")
            write_mock_compiler(compiler)

            result = cnxt_run.run_package(
                manifest,
                bin_name="missing",
                skip_fetch=True,
                compiler=str(compiler),
            )
            self.assertFalse(result.ok)
            self.assertIn("CNXT7103", diag_codes(result))


if __name__ == "__main__":
    unittest.main()
