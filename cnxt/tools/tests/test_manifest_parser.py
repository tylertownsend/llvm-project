from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "manifest_parser.py"
SPEC = importlib.util.spec_from_file_location("manifest_parser", MODULE_PATH)
assert SPEC and SPEC.loader
manifest_parser = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = manifest_parser
SPEC.loader.exec_module(manifest_parser)


def write_manifest(tmp: Path, content: str) -> Path:
    path = tmp / "Cnxt.toml"
    path.write_text(content, encoding="utf-8")
    return path


def codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


class ManifestParserTests(unittest.TestCase):
    def test_valid_minimal_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = write_manifest(
                tmp,
                """
manifest-version = 1

[package]
name = "demo"
version = "0.1.0"
edition = "cnxt1"
""",
            )

            result = manifest_parser.parse_manifest_file(manifest)
            self.assertTrue(result.ok)
            self.assertEqual([], result.diagnostics)

    def test_missing_package_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            manifest = write_manifest(Path(tmp_str), "manifest-version = 1\n")
            result = manifest_parser.parse_manifest_file(manifest)
            self.assertIn("CNXT1001", codes(result))

    def test_unknown_top_level_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            manifest = write_manifest(
                Path(tmp_str),
                """
manifest-version = 1
unknown = true

[package]
name = "demo"
version = "0.1.0"
edition = "cnxt1"
""",
            )
            result = manifest_parser.parse_manifest_file(manifest)
            self.assertIn("CNXT1003", codes(result))

    def test_invalid_manifest_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            manifest = write_manifest(
                Path(tmp_str),
                """
manifest-version = 2

[package]
name = "demo"
version = "0.1.0"
edition = "cnxt1"
""",
            )
            result = manifest_parser.parse_manifest_file(manifest)
            self.assertIn("CNXT1008", codes(result))

    def test_dependency_requires_single_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            manifest = write_manifest(
                Path(tmp_str),
                """
manifest-version = 1

[package]
name = "demo"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
bad = { version = "^1.0.0", path = "../bad" }
""",
            )
            result = manifest_parser.parse_manifest_file(manifest)
            self.assertIn("CNXT1005", codes(result))

    def test_dependency_path_cannot_escape_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            manifest = write_manifest(
                Path(tmp_str),
                """
manifest-version = 1

[package]
name = "demo"
version = "0.1.0"
edition = "cnxt1"

[dependencies]
bad = { path = "../outside" }
""",
            )
            result = manifest_parser.parse_manifest_file(manifest)
            self.assertIn("CNXT1006", codes(result))

    def test_dev_dependency_optional_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            manifest = write_manifest(
                Path(tmp_str),
                """
manifest-version = 1

[package]
name = "demo"
version = "0.1.0"
edition = "cnxt1"

[dev-dependencies]
bad = { version = "^1.0.0", optional = true }
""",
            )
            result = manifest_parser.parse_manifest_file(manifest)
            self.assertIn("CNXT1005", codes(result))

    def test_parse_error_is_structured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            manifest = write_manifest(Path(tmp_str), "manifest-version =\n")
            result = manifest_parser.parse_manifest_file(manifest)
            self.assertFalse(result.ok)
            self.assertEqual({"CNXT1002"}, codes(result))


if __name__ == "__main__":
    unittest.main()
