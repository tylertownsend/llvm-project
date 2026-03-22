from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


TOOLS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOLS_DIR.parents[1]
STARTER_TEMPLATE_DIR = REPO_ROOT / "cnxt" / "examples" / "starter" / "hello-app"
CLANGXX = Path(
    os.environ.get(
        "CNXT_TEST_CLANGXX",
        str(REPO_ROOT / "build" / "bin" / "clang++"),
    )
)


def _load_module(name: str, filename: str):
    module_path = TOOLS_DIR / filename
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cnxt_run = _load_module("cnxt_run_starter_e2e", "cnxt_run.py")


@unittest.skipUnless(CLANGXX.exists() and sys.platform.startswith("linux"), "requires repo clang++ on Linux")
class StarterTemplateE2ETests(unittest.TestCase):
    def test_starter_template_runs_without_glue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            project = tmp / "hello-app"
            shutil.copytree(STARTER_TEMPLATE_DIR, project)

            source = project / "src" / "main.cn"
            source_text = source.read_text(encoding="utf-8")
            self.assertNotIn('extern "C"', source_text)
            self.assertNotIn("unsafe extern", source_text)

            result = cnxt_run.run_package(
                project,
                skip_fetch=True,
                compiler=str(CLANGXX),
            )
            self.assertTrue(result.ok, result.diagnostics)
            self.assertEqual(0, result.exit_code)
            self.assertIn("hello, cnxt", result.stdout)


if __name__ == "__main__":
    unittest.main()
