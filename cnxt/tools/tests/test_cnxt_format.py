from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "cnxt_format.py"
SPEC = importlib.util.spec_from_file_location("cnxt_format", MODULE_PATH)
assert SPEC and SPEC.loader
cnxt_format = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cnxt_format
SPEC.loader.exec_module(cnxt_format)


def diag_codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


def write_fake_formatter(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
import json
import os
import pathlib
import sys

payload = {"argv": sys.argv[1:], "stdin": sys.stdin.read()}
pathlib.Path(os.environ["CNXT_FMT_LOG"]).write_text(json.dumps(payload), encoding="utf-8")
sys.stdout.write(payload["stdin"].replace("let  x=1;", "let x = 1;"))
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


class CNxtFormatTests(unittest.TestCase):
    def test_format_text_uses_baseline_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            formatter = tmp / "fake-clang-format.py"
            log_path = tmp / "format-log.json"
            write_fake_formatter(formatter)

            previous = os.environ.get("CNXT_FMT_LOG")
            os.environ["CNXT_FMT_LOG"] = str(log_path)
            try:
                result = cnxt_format.format_text(
                    "let  x=1;\n",
                    filename="main.cn",
                    clang_format=str(formatter),
                )
            finally:
                if previous is None:
                    os.environ.pop("CNXT_FMT_LOG", None)
                else:
                    os.environ["CNXT_FMT_LOG"] = previous

            self.assertTrue(result.ok)
            self.assertTrue(result.changed)
            self.assertEqual("let x = 1;\n", result.text)
            payload = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertIn("--assume-filename", payload["argv"])
            self.assertIn("main.cn", payload["argv"])
            self.assertTrue(any(arg.startswith("--style={BasedOnStyle: LLVM") for arg in payload["argv"]))

    def test_format_text_requires_formatter_binary(self) -> None:
        result = cnxt_format.format_text(
            "let  x=1;\n",
            filename="main.cn",
            clang_format="/tmp/does-not-exist-cnxt-format",
        )
        self.assertFalse(result.ok)
        self.assertIn("CNXT9002", diag_codes(result))

    def test_format_file_check_reports_needed_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            formatter = tmp / "fake-clang-format.py"
            source = tmp / "src" / "main.cn"
            log_path = tmp / "format-log.json"
            write_fake_formatter(formatter)

            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("let  x=1;\n", encoding="utf-8")

            previous = os.environ.get("CNXT_FMT_LOG")
            os.environ["CNXT_FMT_LOG"] = str(log_path)
            try:
                result = cnxt_format.format_file(
                    source,
                    check=True,
                    clang_format=str(formatter),
                )
            finally:
                if previous is None:
                    os.environ.pop("CNXT_FMT_LOG", None)
                else:
                    os.environ["CNXT_FMT_LOG"] = previous

            self.assertFalse(result.ok)
            self.assertTrue(result.changed)
            self.assertIn("CNXT9005", diag_codes(result))
            self.assertEqual("let  x=1;\n", source.read_text(encoding="utf-8"))

    def test_format_file_write_persists_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            formatter = tmp / "fake-clang-format.py"
            source = tmp / "src" / "main.cn"
            log_path = tmp / "format-log.json"
            write_fake_formatter(formatter)

            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("let  x=1;\n", encoding="utf-8")

            previous = os.environ.get("CNXT_FMT_LOG")
            os.environ["CNXT_FMT_LOG"] = str(log_path)
            try:
                result = cnxt_format.format_file(
                    source,
                    write=True,
                    clang_format=str(formatter),
                )
            finally:
                if previous is None:
                    os.environ.pop("CNXT_FMT_LOG", None)
                else:
                    os.environ["CNXT_FMT_LOG"] = previous

            self.assertTrue(result.ok)
            self.assertTrue(result.changed)
            self.assertEqual("let x = 1;\n", source.read_text(encoding="utf-8"))

    def test_unsupported_profile(self) -> None:
        result = cnxt_format.format_text(
            "let x = 1;\n",
            profile="compact",
            clang_format="/tmp/irrelevant",
        )
        self.assertFalse(result.ok)
        self.assertIn("CNXT9001", diag_codes(result))


if __name__ == "__main__":
    unittest.main()
