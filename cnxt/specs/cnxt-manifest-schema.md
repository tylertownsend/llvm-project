# cNxt Manifest Schema (`Cnxt.toml`)

Status: Milestone 4 schema baseline (`manifest-version = 1`).

This document is the source of truth for `Cnxt.toml` structure and validation
rules used by the cNxt package manager.

## Root Keys

Allowed top-level keys:

- `manifest-version` (required)
- `package` (required)
- `dependencies` (optional)
- `dev-dependencies` (optional)
- `targets` (optional)
- `profile` (optional)
- `workspace` (optional, root-workspace manifests only)

Unknown top-level keys are rejected.

## `manifest-version`

- Type: integer
- Required: yes
- Allowed values: `1`

## `[package]`

Required keys:

- `name` (string): package name, regex `^[a-z][a-z0-9_-]*$`
- `version` (string): semantic version `MAJOR.MINOR.PATCH`
- `edition` (string): currently only `cnxt1`

Optional keys:

- `description` (string)
- `license` (string)
- `repository` (string URL)
- `type` (string): `bin`, `lib`, or `mixed` (default: `mixed`)
- `authors` (array of strings)

## `[dependencies]` and `[dev-dependencies]`

Each entry maps dependency name to either:

1. a version requirement string, for example:
   - `json = "^1.4.0"`
2. an inline table, for example:
   - `json = { version = "^1.4.0", optional = true }`
   - `utils = { path = "../utils" }`
   - `net = { git = "https://example.com/net.git", rev = "deadbeef" }`

Dependency inline-table keys:

- Source keys (exactly one required):
  - `version` (string, semver requirement)
  - `path` (string, relative path)
  - `git` (string URL)
- Git reference keys (optional, at most one):
  - `rev` (string)
  - `tag` (string)
  - `branch` (string)
- Other keys:
  - `optional` (bool, default `false`)
  - `features` (array of strings)
  - `package` (string; alternate package name when the dependency key is an alias)

Validation rules:

- dependency key name regex: `^[a-z][a-z0-9_-]*$`
- `path` must be relative and must not escape the workspace root
- `git` requires `https://` or `ssh://` URL format
- `optional = true` is not allowed in `dev-dependencies`

## `[targets]`

Optional explicit target layout.

Allowed subsections:

- `[targets.lib]` (single table)
- `[[targets.bin]]` (array of tables)
- `[[targets.test]]` (array of tables)

Common target keys:

- `name` (string; required for `bin` and `test`)
- `path` (string; required)
- `required-features` (array of strings, optional)

Validation rules:

- `path` must end with `.cn` or `.cnxt`
- target names must be unique per target kind
- all target paths are relative to the manifest directory

Default behavior when `[targets]` is absent:

- `src/lib.cn` if present is treated as library target
- `src/main.cn` if present is treated as binary target named after package

## `[profile]`

Optional build profile overrides.

Allowed subsections:

- `[profile.debug]`
- `[profile.release]`

Allowed keys per profile:

- `opt-level` (integer `0..3`)
- `debug` (bool)
- `lto` (bool)
- `panic` (string: `abort` or `unwind`)

## `[workspace]`

Optional workspace root metadata.

Allowed keys:

- `members` (array of relative paths; required if `workspace` exists)
- `exclude` (array of relative paths; optional)

Validation rules:

- package manifests inside a workspace must not redefine `[workspace]`
- member paths must contain a `Cnxt.toml`

## Validation Diagnostics (M4 Baseline IDs)

- `CNXT1001`: missing required key
- `CNXT1002`: invalid value type
- `CNXT1003`: unknown key
- `CNXT1004`: invalid semantic version or version requirement
- `CNXT1005`: invalid dependency source specification
- `CNXT1006`: invalid path (absolute, escapes root, or missing file)
- `CNXT1007`: duplicate target name
- `CNXT1008`: unsupported edition or manifest version

## Minimal Example

```toml
manifest-version = 1

[package]
name = "hello-cnxt"
version = "0.1.0"
edition = "cnxt1"
type = "bin"

[dependencies]
http = "^1.2.0"
utils = { path = "../utils" }

[[targets.bin]]
name = "hello-cnxt"
path = "src/main.cn"

[profile.release]
opt-level = 3
lto = true
panic = "abort"
```
