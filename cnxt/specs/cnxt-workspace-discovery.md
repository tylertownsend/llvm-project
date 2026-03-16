# cNxt Workspace Discovery Baseline

Status: Milestone 4 workspace/project-root discovery baseline.

`cnxt/tools/workspace_discovery.py` defines how command entry points resolve
`Cnxt.toml` when invoked from arbitrary paths.

## Resolution Rules

1. Start from input path (or current working directory when omitted).
2. Walk upward to filesystem root, collecting directories containing `Cnxt.toml`.
3. Use the nearest discovered manifest as `package_manifest`.
4. If an ancestor manifest declares `[workspace]` and includes the package path
   in `workspace.members`, treat that manifest as `workspace_root_manifest`.
5. If no manifest is found, report `CNXT8001`.

## Input Handling

- directory input: discover from that directory
- `Cnxt.toml` file input: use as package manifest and still discover workspace root
- invalid/missing path input: report `CNXT8002`

## Command Integration

`cnxt build`, `cnxt run`, and `cnxt test` consume discovery results so users can
run commands from package roots, workspace members, or nested subdirectories
without manually passing absolute manifest paths.
