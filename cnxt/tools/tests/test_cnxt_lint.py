from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "cnxt_lint.py"
SPEC = importlib.util.spec_from_file_location("cnxt_lint", MODULE_PATH)
assert SPEC and SPEC.loader
cnxt_lint = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cnxt_lint
SPEC.loader.exec_module(cnxt_lint)


def diag_codes(result) -> set[str]:
    return {diag.code for diag in result.diagnostics}


class CNxtLintTests(unittest.TestCase):
    def test_lint_text_reports_restricted_constructs(self) -> None:
        code = """
#include "dep.cn"
fn main() {
  for(int i = 0; i < 1; ++i) {}
  let p = new Obj();
  throw 1;
  try {} catch (...) {}
}
template <typename T> struct Box {};
"""
        result = cnxt_lint.lint_text(code, path="main.cn")
        self.assertFalse(result.ok)
        self.assertEqual(
            {"CNXT9101", "CNXT9102", "CNXT9103", "CNXT9104", "CNXT9105"},
            diag_codes(result),
        )
        include_diag = next(diag for diag in result.diagnostics if diag.code == "CNXT9101")
        self.assertIsNotNone(include_diag.fix)
        assert include_diag.fix is not None
        self.assertEqual('import "dep.cn";', include_diag.fix.replacement)

    def test_lint_ignores_comments_and_strings(self) -> None:
        code = """
fn main() {
  // #include "ignored"
  // for(int i = 0; i < 1; ++i) {}
  let s = "throw new delete template <T>";
  /* try { } catch (...) { } */
}
"""
        result = cnxt_lint.lint_text(code, path="main.cn")
        self.assertTrue(result.ok)
        self.assertEqual(set(), diag_codes(result))

    def test_lint_file_reports_line_and_column(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            source = tmp / "main.cn"
            source.write_text(
                "fn main() {\n"
                "  for(int i = 0; i < 1; ++i) {}\n"
                "}\n",
                encoding="utf-8",
            )
            result = cnxt_lint.lint_file(source)
            self.assertFalse(result.ok)
            self.assertEqual({"CNXT9102"}, diag_codes(result))
            self.assertEqual(2, result.diagnostics[0].line)
            self.assertEqual(3, result.diagnostics[0].column)

    def test_lint_paths_expands_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            src = tmp / "src"
            src.mkdir(parents=True, exist_ok=True)
            (src / "main.cn").write_text("fn main() { throw 1; }\n", encoding="utf-8")
            (src / "notes.txt").write_text("#include <ignored>\n", encoding="utf-8")

            result = cnxt_lint.lint_paths([str(tmp)])
            self.assertFalse(result.ok)
            self.assertEqual({"CNXT9104"}, diag_codes(result))
            self.assertEqual(1, len(result.diagnostics))

    def test_missing_file_reports_cnxt9100(self) -> None:
        result = cnxt_lint.lint_file("/tmp/does-not-exist-cnxt-lint.cn")
        self.assertFalse(result.ok)
        self.assertEqual({"CNXT9100"}, diag_codes(result))

    def test_apply_fixes_rewrites_safe_include(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            source = tmp / "main.cn"
            source.write_text(
                '#include "dep.cn"\n'
                "fn main() { throw 1; }\n",
                encoding="utf-8",
            )

            result = cnxt_lint.lint_file(source, apply_fixes=True)
            self.assertFalse(result.ok)
            self.assertEqual(1, result.applied_fixes)
            self.assertEqual({"CNXT9104"}, diag_codes(result))
            self.assertEqual('import "dep.cn";\nfn main() { throw 1; }\n', source.read_text(encoding="utf-8"))

    def test_apply_fixes_over_paths_counts_rewrites(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            src = tmp / "src"
            src.mkdir(parents=True, exist_ok=True)
            (src / "a.cn").write_text('#include "a.cn"\n', encoding="utf-8")
            (src / "b.cn").write_text('#include "b.cn"\n', encoding="utf-8")

            result = cnxt_lint.lint_paths([str(src)], apply_fixes=True)
            self.assertTrue(result.ok)
            self.assertEqual(2, result.applied_fixes)
            self.assertEqual(set(), diag_codes(result))


if __name__ == "__main__":
    unittest.main()
