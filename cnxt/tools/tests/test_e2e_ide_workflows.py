from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


TOOLS_DIR = Path(__file__).resolve().parents[1]


def _load_module(name: str, filename: str):
    module_path = TOOLS_DIR / filename
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cnxt_build = _load_module("cnxt_build_e2e", "cnxt_build.py")
cnxt_format = _load_module("cnxt_format_e2e", "cnxt_format.py")
cnxt_lint = _load_module("cnxt_lint_e2e", "cnxt_lint.py")


def write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fake_formatter(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
import sys
source = sys.stdin.read()
sys.stdout.write(source.replace("let  x=1;", "let x = 1;"))
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


class IDEWorkflowE2ETests(unittest.TestCase):
    def test_project_ide_flow_format_lint_fix_and_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            project = tmp / "app"
            manifest = project / "Cnxt.toml"
            source = project / "src" / "main.cn"
            formatter = tmp / "fake-clang-format.py"

            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "ide-app"
version = "0.1.0"
edition = "cnxt1"
""",
            )
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(
                '#include "dep.cn"\n'
                "fn main() {\n"
                "  let  x=1;\n"
                "  throw 1;\n"
                "}\n",
                encoding="utf-8",
            )
            write_fake_formatter(formatter)

            format_result = cnxt_format.format_file(
                source,
                write=True,
                clang_format=str(formatter),
            )
            self.assertTrue(format_result.ok)
            self.assertTrue(format_result.changed)

            lint_result = cnxt_lint.lint_file(source, apply_fixes=True)
            self.assertFalse(lint_result.ok)
            self.assertEqual(1, lint_result.applied_fixes)
            self.assertEqual({"CNXT9104"}, {diag.code for diag in lint_result.diagnostics})

            updated_source = source.read_text(encoding="utf-8")
            self.assertIn('import "dep.cn";', updated_source)
            self.assertIn("let x = 1;", updated_source)

            build_result = cnxt_build.run_build(manifest, dry_run=True, skip_fetch=True)
            self.assertTrue(build_result.ok)
            self.assertIsNotNone(build_result.compile_commands_path)
            assert build_result.compile_commands_path is not None
            compile_commands_path = Path(build_result.compile_commands_path)
            self.assertTrue(compile_commands_path.exists())
            payload = json.loads(compile_commands_path.read_text(encoding="utf-8"))
            self.assertEqual(1, len(payload))
            self.assertIn("-x cnxt", payload[0]["command"])
            self.assertIn("-std=cnxt1", payload[0]["command"])
            self.assertIn("-fcnxt-ownership-runtime=", payload[0]["command"])

    def test_workspace_member_path_runs_ide_build_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            workspace_manifest = tmp / "Cnxt.toml"
            member_manifest = tmp / "app" / "Cnxt.toml"
            member_source = tmp / "app" / "src" / "main.cn"

            write_manifest(
                workspace_manifest,
                """
manifest-version = 1

[workspace]
members = ["app"]
""",
            )
            write_manifest(
                member_manifest,
                """
manifest-version = 1

[package]
name = "ws-app"
version = "0.1.0"
edition = "cnxt1"
""",
            )
            member_source.parent.mkdir(parents=True, exist_ok=True)
            member_source.write_text("fn main() {}\n", encoding="utf-8")

            result = cnxt_build.run_build(tmp / "app", dry_run=True, skip_fetch=True)
            self.assertTrue(result.ok)
            self.assertIsNotNone(result.compile_commands_path)


if __name__ == "__main__":
    unittest.main()
