from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "cache_layout.py"
SPEC = importlib.util.spec_from_file_location("cache_layout", MODULE_PATH)
assert SPEC and SPEC.loader
cache_layout = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cache_layout
SPEC.loader.exec_module(cache_layout)


def write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def diag_codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


class CacheLayoutTests(unittest.TestCase):
    def test_initialize_creates_default_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "root"
version = "0.1.0"
edition = "cnxt1"
""",
            )

            layout = cache_layout.initialize_cache_layout(manifest)
            self.assertEqual(str(manifest.parent / ".cnxt" / "cache"), layout.root)
            self.assertTrue(Path(layout.root).is_dir())
            self.assertTrue(Path(layout.registry_packages).is_dir())
            self.assertTrue(Path(layout.git_checkouts).is_dir())
            self.assertTrue(Path(layout.git_sources).is_dir())
            self.assertTrue(Path(layout.temp).is_dir())
            self.assertTrue(Path(layout.locks).is_dir())

    def test_registry_and_git_keys_are_stable(self) -> None:
        reg_a = cache_layout.registry_cache_key("json", "^1.4.0")
        reg_b = cache_layout.registry_cache_key("json", "^1.4.0")
        reg_c = cache_layout.registry_cache_key("json", "^2.0.0")
        self.assertEqual(reg_a, reg_b)
        self.assertNotEqual(reg_a, reg_c)

        git_a = cache_layout.git_cache_key("https://example.com/net.git", "deadbeef")
        git_b = cache_layout.git_cache_key("https://example.com/net.git", "deadbeef")
        git_c = cache_layout.git_cache_key("https://example.com/net.git", "cafebabe")
        self.assertEqual(git_a, git_b)
        self.assertNotEqual(git_a, git_c)

    def test_plans_entries_from_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "root"
version = "0.1.0"
edition = "cnxt1"
""",
            )

            lockfile = {
                "lockfile-version": 1,
                "root-manifest": "Cnxt.toml",
                "root-package": "root",
                "constraints": {"json": ["^1.4.0"]},
                "packages": [
                    {
                        "name": "root",
                        "version": "0.1.0",
                        "manifest-path": "Cnxt.toml",
                        "dependencies": [
                            {"name": "json", "source": "version", "requirement": "^1.4.0"},
                            {
                                "name": "net",
                                "source": "git",
                                "git": "https://example.com/net.git",
                                "rev": "deadbeef",
                            },
                            {"name": "utils", "source": "path", "path": "../utils"},
                        ],
                    }
                ],
            }
            lock_path = manifest.parent / "Cnxt.lock"
            lock_path.write_text(json.dumps(lockfile, indent=2), encoding="utf-8")

            result = cache_layout.plan_cache(manifest, initialize=True)
            self.assertTrue(result.ok)
            self.assertEqual(2, len(result.entries))
            self.assertEqual({"git", "version"}, {entry.source for entry in result.entries})
            self.assertEqual({"json", "net"}, {entry.package for entry in result.entries})

    def test_invalid_lockfile_json_reports_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            write_manifest(
                manifest,
                """
manifest-version = 1

[package]
name = "root"
version = "0.1.0"
edition = "cnxt1"
""",
            )
            lock_path = manifest.parent / "Cnxt.lock"
            lock_path.write_text("{ not-json", encoding="utf-8")

            result = cache_layout.plan_cache(manifest)
            self.assertFalse(result.ok)
            self.assertIn("CNXT5002", diag_codes(result))


if __name__ == "__main__":
    unittest.main()
