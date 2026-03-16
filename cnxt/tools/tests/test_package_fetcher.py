from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "package_fetcher.py"
SPEC = importlib.util.spec_from_file_location("package_fetcher", MODULE_PATH)
assert SPEC and SPEC.loader
package_fetcher = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = package_fetcher
SPEC.loader.exec_module(package_fetcher)


def run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def diag_codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


class PackageFetcherTests(unittest.TestCase):
    def test_fetch_registry_and_git_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            lockfile = tmp / "root" / "Cnxt.lock"
            registry_root = tmp / "registry"
            repo = tmp / "net-repo"

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

            run_git(["init"], cwd=tmp)
            run_git(["init", str(repo)], cwd=tmp)
            (repo / "README.md").write_text("net package\n", encoding="utf-8")
            run_git(["-C", str(repo), "add", "README.md"], cwd=tmp)
            run_git(
                [
                    "-C",
                    str(repo),
                    "-c",
                    "user.name=Test User",
                    "-c",
                    "user.email=test@example.com",
                    "commit",
                    "-m",
                    "init",
                ],
                cwd=tmp,
            )
            rev = run_git(["-C", str(repo), "rev-parse", "HEAD"], cwd=tmp)

            (registry_root / "index").mkdir(parents=True, exist_ok=True)
            (registry_root / "artifacts" / "json-1.0.0").mkdir(parents=True, exist_ok=True)
            (registry_root / "artifacts" / "json-1.5.0").mkdir(parents=True, exist_ok=True)
            (registry_root / "artifacts" / "json-1.0.0" / "payload.txt").write_text(
                "json 1.0.0\n", encoding="utf-8"
            )
            (registry_root / "artifacts" / "json-1.5.0" / "payload.txt").write_text(
                "json 1.5.0\n", encoding="utf-8"
            )
            (registry_root / "index" / "json.json").write_text(
                json.dumps(
                    {
                        "versions": [
                            {"version": "1.0.0", "source": "artifacts/json-1.0.0"},
                            {"version": "1.5.0", "source": "artifacts/json-1.5.0"},
                        ]
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            lock_payload = {
                "lockfile-version": 1,
                "root-manifest": "Cnxt.toml",
                "root-package": "root",
                "constraints": {"json": ["^1.0.0"]},
                "packages": [
                    {
                        "name": "root",
                        "version": "0.1.0",
                        "manifest-path": "Cnxt.toml",
                        "dependencies": [
                            {"name": "json", "source": "version", "requirement": "^1.0.0"},
                            {"name": "net", "source": "git", "git": str(repo), "rev": rev},
                        ],
                    }
                ],
            }
            lockfile.write_text(json.dumps(lock_payload, indent=2), encoding="utf-8")

            result = package_fetcher.fetch_packages(manifest, registry=registry_root)
            self.assertTrue(result.ok)
            self.assertEqual(2, len(result.records))
            by_source = {record.source: record for record in result.records}
            self.assertIn("version", by_source)
            self.assertIn("git", by_source)

            version_record = by_source["version"]
            meta_path = Path(version_record.path) / "meta.json"
            self.assertTrue(meta_path.exists())
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertEqual("1.5.0", meta["resolved-version"])

            git_record = by_source["git"]
            self.assertTrue((Path(git_record.path) / "README.md").exists())

    def test_missing_registry_index_reports_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            lockfile = tmp / "root" / "Cnxt.lock"
            registry_root = tmp / "registry"

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
            lockfile.write_text(
                json.dumps(
                    {
                        "lockfile-version": 1,
                        "root-manifest": "Cnxt.toml",
                        "root-package": "root",
                        "constraints": {"missing": ["^1.0.0"]},
                        "packages": [
                            {
                                "name": "root",
                                "version": "0.1.0",
                                "manifest-path": "Cnxt.toml",
                                "dependencies": [
                                    {
                                        "name": "missing",
                                        "source": "version",
                                        "requirement": "^1.0.0",
                                    }
                                ],
                            }
                        ],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            result = package_fetcher.fetch_packages(manifest, registry=registry_root)
            self.assertFalse(result.ok)
            self.assertIn("CNXT6003", diag_codes(result))

    def test_second_fetch_uses_cached_registry_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            manifest = tmp / "root" / "Cnxt.toml"
            lockfile = tmp / "root" / "Cnxt.lock"
            registry_root = tmp / "registry"

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
            (registry_root / "index").mkdir(parents=True, exist_ok=True)
            (registry_root / "artifacts" / "json-1.0.0").mkdir(parents=True, exist_ok=True)
            (registry_root / "artifacts" / "json-1.0.0" / "payload.txt").write_text(
                "json 1.0.0\n", encoding="utf-8"
            )
            (registry_root / "index" / "json.json").write_text(
                json.dumps(
                    {"versions": [{"version": "1.0.0", "source": "artifacts/json-1.0.0"}]},
                    indent=2,
                ),
                encoding="utf-8",
            )
            lockfile.write_text(
                json.dumps(
                    {
                        "lockfile-version": 1,
                        "root-manifest": "Cnxt.toml",
                        "root-package": "root",
                        "constraints": {"json": ["^1.0.0"]},
                        "packages": [
                            {
                                "name": "root",
                                "version": "0.1.0",
                                "manifest-path": "Cnxt.toml",
                                "dependencies": [
                                    {"name": "json", "source": "version", "requirement": "^1.0.0"}
                                ],
                            }
                        ],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            first = package_fetcher.fetch_packages(manifest, registry=registry_root)
            second = package_fetcher.fetch_packages(manifest, registry=registry_root)
            self.assertTrue(first.ok)
            self.assertTrue(second.ok)
            self.assertEqual("fetched", first.records[0].status)
            self.assertEqual("cached", second.records[0].status)


if __name__ == "__main__":
    unittest.main()
