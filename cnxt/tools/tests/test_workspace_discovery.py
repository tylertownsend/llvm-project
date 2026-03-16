from __future__ import annotations

import importlib.util
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


workspace_discovery = load_module("workspace_discovery", "workspace_discovery.py")
cnxt_build = load_module("cnxt_build", "cnxt_build.py")
cnxt_run = load_module("cnxt_run", "cnxt_run.py")
cnxt_test = load_module("cnxt_test", "cnxt_test.py")


def write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def diag_codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


class WorkspaceDiscoveryTests(unittest.TestCase):
    def test_discovers_workspace_root_and_member_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            root_manifest = tmp / "ws" / "Cnxt.toml"
            member_manifest = tmp / "ws" / "members" / "app" / "Cnxt.toml"
            nested = tmp / "ws" / "members" / "app" / "src"

            write_manifest(
                root_manifest,
                """
manifest-version = 1

[package]
name = "workspace-root"
version = "0.1.0"
edition = "cnxt1"

[workspace]
members = ["members/app"]
""",
            )
            write_manifest(
                member_manifest,
                """
manifest-version = 1

[package]
name = "app"
version = "0.1.0"
edition = "cnxt1"
""",
            )
            nested.mkdir(parents=True, exist_ok=True)

            result = workspace_discovery.discover_workspace(nested)
            self.assertTrue(result.ok)
            self.assertEqual(str(member_manifest), result.package_manifest)
            self.assertEqual(str(root_manifest), result.workspace_root_manifest)

    def test_resolve_manifest_input_reports_missing_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            result = workspace_discovery.resolve_manifest_input(Path(tmp_str))
            self.assertFalse(result.ok)
            self.assertIn("CNXT8001", diag_codes(result))

    def test_build_run_test_accept_directory_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            source = tmp / "root" / "src" / "main.cn"
            binary = tmp / "root" / "target" / "debug" / "demo"
            test_bin = tmp / "root" / "target" / "debug" / "smoke.test"

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

            build_result = cnxt_build.run_build(manifest.parent, dry_run=True, skip_fetch=True)
            self.assertTrue(build_result.ok)

            binary.parent.mkdir(parents=True, exist_ok=True)
            binary.write_text("#!/usr/bin/env bash\necho demo\n", encoding="utf-8")
            binary.chmod(0o755)

            run_result = cnxt_run.run_package(manifest.parent, skip_build=True)
            self.assertTrue(run_result.ok)
            self.assertEqual("demo", run_result.stdout.strip())

            test_bin.write_text("#!/usr/bin/env bash\necho ok\n", encoding="utf-8")
            test_bin.chmod(0o755)

            test_result = cnxt_test.run_tests(manifest.parent, skip_build=True)
            self.assertTrue(test_result.ok)
            self.assertEqual(1, len(test_result.executions))


if __name__ == "__main__":
    unittest.main()
