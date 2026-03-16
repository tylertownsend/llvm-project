# cNxt Local Cache Layout (`.cnxt/cache`)

Status: Milestone 4 local-cache baseline.

This document defines the local cache directory structure used for downloaded
packages and source checkouts.

## Root Location

Default cache root for a project:

```text
<project-root>/.cnxt/cache
```

`cache_root` may be overridden by tooling flags/environment in future
deliverables.

## Directory Structure

```text
.cnxt/cache/
  registry/
    packages/      # resolved version-source package payloads
  git/
    sources/       # bare/source mirror clones by repository URL
    checkouts/     # revision-specific working trees
  tmp/             # transient download/extract workdir
  locks/           # per-key lockfiles for concurrent cache writes
```

## Keying Rules

All cache keys are deterministic and content-addressable from dependency
metadata:

- Registry key input: `registry-id | package-name | version-requirement`
- Git checkout key input: `git-url | ref` where `ref` is `rev`, `tag`,
  `branch`, or `HEAD`
- Git source mirror key input: `git-url`

Keys use lowercase hex SHA-256 digests truncated to 16 characters.

## Planning Rules

- `path` dependencies do not produce download cache entries.
- `version` dependencies map to `registry/packages/<package>-<key>`.
- `git` dependencies map to `git/checkouts/<key>`.
- Duplicate dependencies across packages are deduplicated by cache key.
