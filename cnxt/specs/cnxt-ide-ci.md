# cNxt IDE CI Integration

This document defines the baseline CI slice for cNxt IDE-quality tooling.

## Workflow

- GitHub Actions workflow: `.github/workflows/cnxt-ide-integration.yml`
- Trigger paths:
  - `cnxt/**`
  - `.github/workflows/cnxt-ide-integration.yml`
- Matrix:
  - Python `3.8`
  - Python `3.11`

## Test Coverage in CI

- `cnxt/tools/tests/test_cnxt_format.py`
  - formatter profile behavior and command integration.
- `cnxt/tools/tests/test_cnxt_lint.py`
  - policy diagnostics and safe fix-it behavior.
- `cnxt/tools/tests/test_e2e_ide_workflows.py`
  - representative project flow:
    - format source
    - apply safe lint fix-it
    - generate `compile_commands.json` via `cnxt build --dry-run`
  - workspace-member entrypoint behavior for build/IDE flows.
