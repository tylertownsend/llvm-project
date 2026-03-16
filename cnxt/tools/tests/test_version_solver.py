from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "version_solver.py"
SPEC = importlib.util.spec_from_file_location("version_solver", MODULE_PATH)
assert SPEC and SPEC.loader
version_solver = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = version_solver
SPEC.loader.exec_module(version_solver)


def write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def diag_codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


class VersionSolverTests(unittest.TestCase):
    def test_caret_semver_zero_major_range(self) -> None:
        req = version_solver.parse_requirement_to_range("^0.2.3")
        assert req is not None
        self.assertTrue(req.contains(version_solver.Version.parse("0.2.3")))
        self.assertTrue(req.contains(version_solver.Version.parse("0.2.9")))
        self.assertFalse(req.contains(version_solver.Version.parse("0.3.0")))

    def test_compatible_constraints_succeed(self) -> None:
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
foo = ">=1.2.0"
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

[dependencies]
foo = "<2.0.0"
""",
            )

            result = version_solver.solve_versions(root_manifest)
            self.assertTrue(result.ok)
            self.assertEqual({"foo"}, set(result.constraints))
            self.assertEqual({"<2.0.0", ">=1.2.0"}, set(result.constraints["foo"]))

    def test_conflicting_constraints_emit_cnxt3002(self) -> None:
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
foo = ">=2.0.0"
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

[dependencies]
foo = "<2.0.0"
""",
            )

            result = version_solver.solve_versions(root_manifest)
            self.assertIn("CNXT3002", diag_codes(result))

    def test_local_version_mismatch_emit_cnxt3001(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            root_manifest = tmp / "root" / "Cnxt.toml"
            foo_manifest = tmp / "foo" / "Cnxt.toml"

            write_manifest(
                root_manifest,
                """
manifest-version = 1

[package]
name = "root"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
foo-local = { path = "../foo", package = "foo" }
foo = "^2.0.0"
""",
            )
            write_manifest(
                foo_manifest,
                """
manifest-version = 1

[package]
name = "foo"
version = "1.5.0"
edition = "cnxt1"
""",
            )

            result = version_solver.solve_versions(root_manifest)
            self.assertIn("CNXT3001", diag_codes(result))

    def test_invalid_requirement_emit_cnxt3003(self) -> None:
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
foo = "latest"
""",
            )

            result = version_solver.solve_versions(root_manifest)
            self.assertIn("CNXT3003", diag_codes(result))


if __name__ == "__main__":
    unittest.main()
