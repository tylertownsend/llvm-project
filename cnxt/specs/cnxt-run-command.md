# cNxt Run Command Baseline (`cnxt run`)

Status: Milestone 4 run-command baseline.

`cnxt/tools/cnxt_run.py` provides a baseline workflow for running cNxt binaries.

## Flow

Default behavior:

1. invoke `cnxt build` workflow
2. select a binary target (`--bin` or first built binary)
3. execute binary with forwarded arguments

Because `cnxt build` now stages the ownership runtime beside built cNxt
binaries/tests and links them with an `$ORIGIN` rpath, starter-layout projects
do not need manual runtime flags or `LD_LIBRARY_PATH` during `cnxt run`.

With `--skip-build`, the command runs an existing artifact from:

```text
target/<profile>/<bin-name>
```

where `<bin-name>` is `--bin` or package name from `Cnxt.toml`.

## Diagnostics

- `CNXT7101`: binary name cannot be determined
- `CNXT7102`: runnable binary artifact missing
- `CNXT7103`: requested binary was not built
- `CNXT7104`: runtime execution failure (non-zero exit or non-executable)
