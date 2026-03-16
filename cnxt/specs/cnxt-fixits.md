# cNxt Safe Fix-Its (v1)

This document defines safe automatic fix-its provided by
`cnxt/tools/cnxt_lint.py --apply-fixes`.

## Safety Policy

- Fix-its are applied only when transformation is syntax-preserving and
  unambiguous.
- Rules without guaranteed-safe rewrites remain diagnostic-only.

## Supported Fix-Its

- `CNXT9101` textual include (`#include "path"`)
  - rewrite: `import "path";`
  - scope: quoted include lines that match the full line pattern.

## Non-Automated Diagnostics (v1)

- `CNXT9102` C-style `for(...)`
- `CNXT9103` `new`/`delete`
- `CNXT9104` `try`/`catch`/`throw`
- `CNXT9105` `template <...>`

These remain manual changes in v1 to avoid unsafe behavior changes.
