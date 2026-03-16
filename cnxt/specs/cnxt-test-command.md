# cNxt Test Command Baseline (`cnxt test`)

Status: Milestone 4 test-command baseline.

`cnxt/tools/cnxt_test.py` provides baseline test orchestration for cNxt
projects.

## Flow

Default behavior:

1. invoke `cnxt build`
2. collect built test artifacts (`kind = test`)
3. execute each test binary
4. report pass/fail with structured diagnostics

With `--skip-build`, existing `*.test` artifacts are loaded from:

```text
target/<profile>/*.test
```

## Diagnostics

- `CNXT7201`: no test targets found
- `CNXT7202`: test binary missing or non-executable
- `CNXT7203`: test process returned non-zero exit code
