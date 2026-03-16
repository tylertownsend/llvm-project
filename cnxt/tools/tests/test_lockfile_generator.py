from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "lockfile_generator.py"
SPEC = importlib.util.spec_from_file_location("lockfile_generator", MODULE_PATH)
assert SPEC and SPEC.loader
lockfile_generator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = lockfile_generator
SPEC.loader.exec_module(lockfile_generator)


def write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def diag_codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


class LockfileGeneratorTests(unittest.TestCase):
    def test_deterministic_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            root_manifest = tmp / "root" / "Cnxt.toml"
            alpha_manifest = tmp / "alpha" / "Cnxt.toml"
            beta_manifest = tmp / "beta" / "Cnxt.toml"

            write_manifest(
                root_manifest,
                """
manifest-version = 1

[package]
name = "root"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
zed = "^3.0.0"
beta-local = { path = "../beta", package = "beta" }
alpha = { path = "../alpha" }
""",
            )
            write_manifest(
                alpha_manifest,
                """
manifest-version = 1

[package]
name = "alpha"
version = "1.2.0"
edition = "cnxt1"

[dependencies]
zed = ">=3.0.0"
""",
            )
            write_manifest(
                beta_manifest,
                """
manifest-version = 1

[package]
name = "beta"
version = "1.0.0"
edition = "cnxt1"

[dependencies]
alpha = { path = "../alpha" }
""",
            )

            first = lockfile_generator.generate_lockfile(root_manifest)
            second = lockfile_generator.generate_lockfile(root_manifest)

            self.assertTrue(first.ok)
            self.assertTrue(second.ok)
            self.assertEqual(first.lockfile, second.lockfile)
            self.assertEqual(
                lockfile_generator.render_lockfile(first.lockfile),
                lockfile_generator.render_lockfile(second.lockfile),
            )
            assert first.lockfile is not None
            self.assertEqual(
                ["alpha", "beta", "root"],
                [pkg["name"] for pkg in first.lockfile["packages"]],
            )
            root_pkg = next(pkg for pkg in first.lockfile["packages"] if pkg["name"] == "root")
            self.assertEqual(
                ["alpha", "beta", "zed"],
                [dep["name"] for dep in root_pkg["dependencies"]],
            )

    def test_conflicting_constraints_fail_lock_generation(self) -> None:
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

            result = lockfile_generator.generate_lockfile(root_manifest)
            self.assertFalse(result.ok)
            self.assertIsNone(result.lockfile)
            self.assertIn("CNXT3002", diag_codes(result))

    def test_write_lockfile_default_location(self) -> None:
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
""",
            )

            result = lockfile_generator.write_lockfile(root_manifest)
            self.assertTrue(result.ok)
            self.assertIsNotNone(result.output_path)
            assert result.output_path is not None
            output_path = Path(result.output_path)
            self.assertEqual(root_manifest.parent / "Cnxt.lock", output_path)
            self.assertTrue(output_path.exists())
            assert result.lockfile is not None
            self.assertEqual(
                lockfile_generator.render_lockfile(result.lockfile),
                output_path.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
