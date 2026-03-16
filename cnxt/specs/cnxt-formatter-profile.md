# cNxt Formatter Baseline Profile

This document defines the baseline formatting profile used by
`cnxt/tools/cnxt_format.py`.

## Profile Name

- `baseline`

## Baseline Style

The baseline profile invokes `clang-format` with this style payload:

```text
{BasedOnStyle: LLVM, IndentWidth: 2, ContinuationIndentWidth: 4, ColumnLimit: 100, BreakBeforeBraces: Stroustrup, AllowShortFunctionsOnASingleLine: Empty, PointerAlignment: Left, SortIncludes: Never}
```

Rules for this milestone:

- cNxt formatter uses one profile (`baseline`) in v1.
- source ordering is stable (`SortIncludes: Never`).
- output is deterministic for identical input text and style.

## Diagnostics

- `CNXT9001`: unsupported formatter profile.
- `CNXT9002`: formatter binary could not be resolved/executed.
- `CNXT9003`: formatter process failed.
- `CNXT9004`: source path does not exist.
- `CNXT9005`: `--check` detected formatting drift.
