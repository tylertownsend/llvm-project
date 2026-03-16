# cNxt Package Fetcher Sources (Milestone 4 Baseline)

Status: Milestone 4 fetcher baseline.

This document defines the source formats consumed by
`cnxt/tools/package_fetcher.py`.

## Inputs

The fetcher reads dependencies from `Cnxt.lock` package dependency entries:

- `source = "version"` with `name` and `requirement`
- `source = "git"` with `name`, `git`, and optional `rev`/`tag`/`branch`

`source = "path"` entries are local and not fetched.

## Registry Source Format

Registry root is a path or URL containing package index files:

```text
<registry-root>/index/<package>.json
```

Index file shape:

```json
{
  "versions": [
    { "version": "1.0.0", "source": "artifacts/pkg-1.0.0" },
    { "version": "1.1.0", "source": "https://..." }
  ]
}
```

Resolution behavior:

- parse lockfile requirement (`^`, `~`, comparators, exact)
- select highest version satisfying the requirement
- fetch/copy the selected `source` into cache

`source` may be:

- relative path under registry root
- absolute/local file path
- `file://`, `http://`, or `https://` URL

## Git Source Behavior

For each unique `(git-url, ref)`:

- maintain a mirror clone under cache `git/sources/`
- materialize checkout under cache `git/checkouts/`
- ref precedence: `rev`, then `tag`, then `branch`, then `HEAD`

## Diagnostics

- `CNXT6003`: registry index/source loading failures
- `CNXT6004`: version requirement cannot be satisfied
- `CNXT6005`: git fetch/checkout failures
