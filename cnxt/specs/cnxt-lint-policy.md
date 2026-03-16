# cNxt Lint Policy (v1)

This document defines the baseline "one obvious way" lint checks implemented by
`cnxt/tools/cnxt_lint.py`.

## Scope

- Lint input files: `.cn`, `.cnxt`, `.cni`.
- Diagnostics are line/column based and deterministic.
- Comment and string contents are ignored for rule matching.

## Rules

- `CNXT9101`: textual include usage (`#include`) is forbidden.
  - Use `import` and package dependencies.
- `CNXT9102`: C-style `for (...)` loop syntax is forbidden.
  - Use the cNxt for-in loop form.
- `CNXT9103`: `new`/`delete` is forbidden.
  - Use `unique/shared/weak` handle-based ownership.
- `CNXT9104`: exception constructs (`try`, `catch`, `throw`) are forbidden.
- `CNXT9105`: `template <...>` declarations are forbidden in cnxt1.

## Tool Diagnostics

- `CNXT9100`: input path error (missing file or no discovered input files).
