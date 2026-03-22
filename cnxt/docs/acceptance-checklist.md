# cNxt Milestone 10 Acceptance Checklist

Milestone 10 is complete only when every item below is true at the same time.

## Release Gate

- `cNxt Compiler Matrix` is green on both `ubuntu-24.04` and `macos-14`.
- The Linux leg of `cNxt Compiler Matrix` passes `Gate no-glue starter app`,
  which runs `cnxt/tools/tests/test_e2e_starter_template.py` against the
  matrix-built `clang++`.
- `cNxt Ownership Runtime Sanitizers` is green on `cnxt/runtime/ownership/`.
- The matrix workflow uploads fresh `cnxt-runtime-baselines-<os>` artifacts for
  Linux and macOS.
- `cnxt/docs/quickstart.md` remains accurate for the starter-template path and
  still requires no handwritten `extern "C"` or `unsafe extern` glue in the
  shipped example sources.

## Required Evidence

- Cross-platform CI workflow:
  `.github/workflows/cnxt-compiler-matrix.yml`
- Runtime sanitizer workflow:
  `.github/workflows/cnxt-ownership-runtime-sanitizers.yml`
- No-glue starter acceptance test:
  `cnxt/tools/tests/test_e2e_starter_template.py`
- Quickstart documentation:
  `cnxt/docs/quickstart.md`
- Current branch-local performance baselines:
  `cnxt/runtime/ownership/benchmarks/ownership_dispatch_bench.cpp`

## Notes

- The acceptance gate is intentionally centered on the starter-template app
  because it represents the intended normal-user package layout
  (`Cnxt.toml` + `src/main.cn`) instead of a one-off compiler invocation.
- The matrix workflow still keeps the broader M6-M9 lit slice alongside the
  starter gate so the no-glue app test is not the only signal.
- Raw-pointer FFI remains outside this acceptance target; those edges are
  governed by `unsafe extern "C"` and the guidance in
  `cnxt/specs/cnxt-ffi-boundary.md`.
