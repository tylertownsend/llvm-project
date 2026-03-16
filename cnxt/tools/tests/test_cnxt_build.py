from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "cnxt_build.py"
SPEC = importlib.util.spec_from_file_location("cnxt_build", MODULE_PATH)
assert SPEC and SPEC.loader
cnxt_build = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cnxt_build
SPEC.loader.exec_module(cnxt_build)


def write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def diag_codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


class CnxtBuildTests(unittest.TestCase):
    def test_dry_run_build_generates_compile_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            source = tmp / "root" / "src" / "main.cn"

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

            result = cnxt_build.run_build(manifest, dry_run=True, skip_fetch=True)
            self.assertTrue(result.ok)
            self.assertIsNotNone(result.compile_commands_path)
            self.assertIsNotNone(result.lockfile_path)
            assert result.compile_commands_path is not None
            compile_commands = Path(result.compile_commands_path)
            self.assertTrue(compile_commands.exists())
            payload = json.loads(compile_commands.read_text(encoding="utf-8"))
            self.assertEqual(1, len(payload))
            self.assertIn("-std=cnxt1", payload[0]["command"])
            self.assertEqual({"bin"}, {artifact.kind for artifact in result.artifacts})

    def test_build_requires_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "empty"
version = "0.1.0"
edition = "cnxt1"
""",
            )

            result = cnxt_build.run_build(manifest, dry_run=True, skip_fetch=True)
            self.assertFalse(result.ok)
            self.assertIn("CNXT7002", diag_codes(result))

    def test_build_executes_with_mock_compiler(self) -> None:
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
            compiler.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
out=""
while [[ $# -gt 0 ]]; do
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
echo "artifact" > "${out}"
""",
                encoding="utf-8",
            )
            compiler.chmod(0o755)

            result = cnxt_build.run_build(
                manifest,
                dry_run=False,
                skip_fetch=True,
                compiler=str(compiler),
            )
            self.assertTrue(result.ok)
            artifact_paths = [Path(artifact.path) for artifact in result.artifacts]
            self.assertTrue(any(path.exists() for path in artifact_paths))


if __name__ == "__main__":
    unittest.main()
