# cNxt Build Command Baseline (`cnxt build`)

Status: Milestone 4 build-command baseline.

`cnxt/tools/cnxt_build.py` defines the initial build orchestration flow:

1. parse/validate `Cnxt.toml`
2. generate deterministic `Cnxt.lock`
3. optionally fetch lockfile dependencies
4. derive build targets (`[targets]` or default `src/main.cn` / `src/lib.cn`)
5. stage the compiler-owned ownership runtime in `target/<profile>/`
6. emit `compile_commands.json`
7. compile/link targets with automatic `-fcnxt-ownership-runtime=...` wiring
   for cNxt inputs (or dry-run plan)

Locked replay mode:

- `--locked` skips lockfile regeneration and requires an existing `Cnxt.lock`
- dependency fetch uses pinned lockfile versions when present

## Profiles

- `debug`: `-O0 -g`
- `release`: `-O2 -DNDEBUG`

## Target Derivation

When `[targets]` is not specified:

- build binary target from `src/main.cn` named after package
- build library object target from `src/lib.cn` named after package
- automatically stage `libcnxt_ownership_rt.so` beside built binaries/tests so
  starter-layout projects run without manual runtime flags or `LD_LIBRARY_PATH`

When `[targets]` is specified:

- `[targets.lib]` -> library object
- `[[targets.bin]]` -> linked binaries
- `[[targets.test]]` -> linked test binaries (`<name>.test`)

## Diagnostics

- `CNXT7001`: manifest/lockfile stage failure
- `CNXT7002`: no build targets discovered
- `CNXT7003`: compiler command failed
- `CNXT7004`: compiler executable not found
- `CNXT7005`: `--locked` requested but lockfile is missing
