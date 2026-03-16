from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "dependency_graph.py"
SPEC = importlib.util.spec_from_file_location("dependency_graph", MODULE_PATH)
assert SPEC and SPEC.loader
dependency_graph = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = dependency_graph
SPEC.loader.exec_module(dependency_graph)


def write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def diag_codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


class DependencyGraphTests(unittest.TestCase):
    def test_acyclic_path_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            root_manifest = tmp / "root" / "Cnxt.toml"
            dep_manifest = tmp / "dep" / "Cnxt.toml"

            write_manifest(
                root_manifest,
                """
manifest-version = 1

[package]
name = "root"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
dep = { path = "../dep" }
""",
            )
            write_manifest(
                dep_manifest,
                """
manifest-version = 1

[package]
name = "dep"
version = "0.1.0"
edition = "cnxt1"
""",
            )

            result = dependency_graph.build_dependency_graph(root_manifest)
            self.assertTrue(result.ok)
            self.assertEqual({("root", "dep")}, set(result.edges))

    def test_missing_path_dependency_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            root_manifest = tmp / "root" / "Cnxt.toml"

            write_manifest(
                root_manifest,
                """
manifest-version = 1

[package]
name = "root"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
missing = { path = "../missing" }
""",
            )

            result = dependency_graph.build_dependency_graph(root_manifest)
            self.assertIn("CNXT2002", diag_codes(result))

    def test_detects_dependency_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            a_manifest = tmp / "a" / "Cnxt.toml"
            b_manifest = tmp / "b" / "Cnxt.toml"

            write_manifest(
                a_manifest,
                """
manifest-version = 1

[package]
name = "a"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
b = { path = "../b" }
""",
            )
            write_manifest(
                b_manifest,
                """
manifest-version = 1

[package]
name = "b"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
a = { path = "../a" }
""",
            )

            result = dependency_graph.build_dependency_graph(a_manifest)
            self.assertIn("CNXT2004", diag_codes(result))

    def test_duplicate_package_name_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            root_manifest = tmp / "root" / "Cnxt.toml"
            dup_manifest = tmp / "dup" / "Cnxt.toml"

            write_manifest(
                root_manifest,
                """
manifest-version = 1

[package]
name = "dup-name"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
dep = { path = "../dup" }
""",
            )
            write_manifest(
                dup_manifest,
                """
manifest-version = 1

[package]
name = "dup-name"
version = "0.2.0"
edition = "cnxt1"
""",
            )

            result = dependency_graph.build_dependency_graph(root_manifest)
            self.assertIn("CNXT2003", diag_codes(result))


if __name__ == "__main__":
    unittest.main()
