# cNxt Lockfile Schema (`Cnxt.lock`)

Status: Milestone 4 lockfile baseline (`lockfile-version = 1`).

This document defines the on-disk lockfile shape produced by
`cnxt/tools/lockfile_generator.py`.

## Goals

- deterministic output for reproducible builds and CI replay
- machine-readable data for downstream build and fetch commands
- explicit linkage to manifest dependency constraints

## Top-Level Shape

`Cnxt.lock` is JSON with the following required keys:

- `lockfile-version` (integer, required): currently `1`
- `root-manifest` (string, required): path to root `Cnxt.toml` relative to root
  manifest directory
- `root-package` (string, required): root package name from `[package].name`
- `packages` (array, required): locked local package entries
- `constraints` (object, required): merged version requirements by package name

## `packages[]`

Each package entry is an object with:

- `name` (string): package name
- `version` (string): semantic version
- `manifest-path` (string): manifest path relative to root manifest directory
- `dependencies` (array): normalized dependency entries

Dependency entry keys:

- `name` (string, required): target package name (after alias/package override resolution)
- `source` (string, required): one of `version`, `path`, `git`, `unknown`
- `requirement` (string, optional): semantic version requirement for version source
- `path` (string, optional): relative path for path source
- `git` (string, optional): git URL for git source
- `rev` / `tag` / `branch` (string, optional): git selector metadata
- `optional` (bool, optional): emitted only when `true`
- `features` (array of strings, optional): sorted feature names

## `constraints`

`constraints` is an object where each key is a package name and each value is an
array of semantic version requirement strings collected by the solver.

## Determinism Rules

Lockfile generation must be deterministic for identical inputs:

- `packages` sorted by package name ascending
- each package `dependencies` sorted by name/source/requirement/path/git refs
- `constraints` keys sorted lexicographically
- each `constraints` value sorted lexicographically
- JSON rendered with stable key ordering and indentation
- no timestamp, host, or environment-specific metadata
