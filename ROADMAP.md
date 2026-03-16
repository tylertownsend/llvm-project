# ROADMAP

Source plan: `cnxt/docs/commit-plan.md`.

## Priority Queue

1. M5-01 Ensure clangd fallback compile commands select cNxt mode.
2. M5-02 Improve completion ranking for cNxt-first constructs and restrictions.
3. M5-03 Add semantic token classification coverage for cNxt files.

## Deliverable Status

- [x] M1-01 through M1-12
- [x] M2-01 through M2-14
- [x] M3-00 through M3-13
- [x] M4-01 through M4-14
- [ ] M5-01 through M5-09

## Completion Log

### 2026-03-15 - M2-09

- Completed item: reject template declarations and template argument use in cNxt mode.
- What changed:
  - parser now rejects `template` declarations when `CNxtNoTemplates` is enabled.
  - template-id annotation now emits a direct cNxt error and marks template arguments invalid in cNxt mode.
  - added parser coverage in `clang/test/Parser/cnxt-templates.cpp`.
- What is now unblocked:
  - M2-10 inheritance restrictions can land independently.
  - M2-11 operator overloading restrictions can land independently.
  - M2-14 recovery-oriented restriction test expansion.
- Direction check:
  - roadmap remains directionally correct; this keeps cNxt as an intentionally restricted C++ subset.

### 2026-03-15 - M2-10

- Completed item: reject inheritance and base-specifier syntax in cNxt mode.
- What changed:
  - parser now rejects base clauses (`: Base`) for cNxt class/struct declarations.
  - parser recovery skips base specifiers and resumes at class body parsing.
  - extended `clang/test/Parser/cnxt-restrictions.cpp` with inheritance coverage.
- What is now unblocked:
  - M2-11 operator overloading restrictions can be implemented without base-clause parser conflicts.
  - M2-14 additional restriction recovery tests can include inheritance scenarios.
- Direction check:
  - roadmap remains directionally correct; cNxt restriction enforcement continues to tighten surface area safely.

### 2026-03-15 - M2-11

- Completed item: reject operator overloading declarations in cNxt mode.
- What changed:
  - semantic analysis now rejects operator-function, literal-operator, and conversion-operator declarations in cNxt mode.
  - added cNxt-specific Sema diagnostic: `err_cnxt_unsupported_declaration`.
  - extended `clang/test/Parser/cnxt-restrictions.cpp` with operator-overload rejection coverage.
- What is now unblocked:
  - M2-12 cast restriction work can proceed with clearer operator surface limits.
  - M2-14 can now include operator-overload recovery assertions.
- Direction check:
  - roadmap remains directionally correct; this prevents C++ operator-surface leakage into cNxt.

### 2026-03-15 - M2-12

- Completed item: restrict C-style casts to explicit `unsafe` regions.
- What changed:
  - semantic cast handling now rejects C-style casts in cNxt mode.
  - added dedicated cNxt Sema diagnostic for unsupported non-declaration features.
  - extended `clang/test/Parser/cnxt-restrictions.cpp` with C-style cast rejection coverage.
- What is now unblocked:
  - M2-13 include-flow policy enforcement is independent and ready.
  - M2-14 recovery tests can include cast-restriction scenarios.
- Direction check:
  - roadmap remains directionally correct; this reduces unsafe C++ escape hatches in cNxt.

### 2026-03-15 - M2-13

- Completed item: reject textual include-based cNxt package flows.
- What changed:
  - preprocessor include handling now emits a cNxt policy error for textual include directives.
  - include directive is discarded after the diagnostic to keep parsing stable.
  - added `clang/test/Preprocessor/cnxt-no-include.c` coverage.
- What is now unblocked:
  - M2-14 can consolidate and harden recovery-oriented restriction tests as the final milestone-2 item.
- Direction check:
  - roadmap remains directionally correct; this reinforces module/import-first cNxt package flow.

### 2026-03-15 - M2-14

- Completed item: add recovery-focused tests for remaining milestone-2 restrictions.
- What changed:
  - added parser recovery coverage in `clang/test/Parser/cnxt-recovery.cpp` spanning template, inheritance, operator-overload, and cast restrictions.
  - extended `clang/test/Preprocessor/cnxt-no-include.c` so verification requires post-include parsing to continue.
- What is now unblocked:
  - milestone 2 is complete; milestone 3 ownership feasibility and vocabulary work can begin.
- Direction check:
  - roadmap remains directionally correct; restriction enforcement now has explicit recovery regression coverage.

### 2026-03-15 - M3-00

- Completed item: feasibility spike for std-backed ownership handles without user memory headers.
- What changed:
  - added `cnxt/docs/m3-00-feasibility.md` with experiment matrix and concrete outcomes.
  - documented current blockers and fallback constraints.
- What is now unblocked:
  - M3-01 ownership vocabulary standardization with evidence-backed assumptions.
  - M3-02 parser/type work for ownership handle spellings.
  - M3-03 prelude/module design with explicit constraints from measured behavior.
- Direction check:
  - roadmap remains directionally correct; the spike confirms feasibility direction but highlights required compiler-owned boundaries.

### 2026-03-15 - M3-01

- Completed item: standardize ownership vocabulary on `unique/shared/weak`.
- What changed:
  - updated `cnxt/README.md` ownership model and roadmap references from `strong` to `unique`.
  - updated milestone-2 scope text to reference `unique<T>` instead of `strong<T>`.
- What is now unblocked:
  - M3-02 parser/type work can target stable ownership spellings.
  - M3-03 prelude design can expose finalized user-facing handle names.
- Direction check:
  - roadmap remains directionally correct; docs now match intended ownership vocabulary.

### 2026-03-15 - M3-02

- Completed item: parse and type-check cNxt ownership handles `unique<T>`, `shared<T>`, and `weak<T>`.
- What changed:
  - parser now treats `unique/shared/weak` template-id spellings as cNxt ownership-handle exceptions instead of generic forbidden template argument lists.
  - compiler-provided ownership-handle declarations were introduced so cNxt handle spellings can type-check without user-authored templates.
  - added parser coverage in `clang/test/Parser/cnxt-ownership.cpp` for accepted handles while preserving rejection of non-handle template-ids and template declarations.
- What is now unblocked:
  - M3-03 can focus on shaping the compiler-owned prelude/injection boundary rather than basic handle name recognition.
  - M3-04 and M3-05 lowering work can target already-parsed and typed handle surfaces.
- Direction check:
  - roadmap remains directionally correct; cNxt now has a compiler-owned ownership type surface while keeping the broader template restrictions in place.

### 2026-03-15 - M3-03

- Completed item: add compiler-owned cNxt prelude/injected ownership declarations.
- What changed:
  - frontend preprocessor initialization now injects a dedicated `<cnxt-prelude>` block that declares `unique<T>`, `shared<T>`, and `weak<T>`.
  - cNxt template-declaration restriction now exempts compiler-prelude locations while preserving user-file template rejection.
  - moved ownership declaration injection out of Sema initialization and into the preprocessor prelude path.
  - added preprocessor coverage in `clang/test/Preprocessor/cnxt-prelude.c` and kept parser restriction coverage green.
- What is now unblocked:
  - M3-04 can lower `unique<T>` with a stable compiler-owned declaration boundary.
  - M3-05 and M3-06 lowering can reuse the same prelude injection mechanism.
- Direction check:
  - roadmap remains directionally correct; ownership handles are now provided through an explicit compiler-owned prelude path rather than ad hoc declaration injection.

### 2026-03-15 - M3-04

- Completed item: lower `unique<T>` to an internal std-backed representation.
- What changed:
  - cNxt prelude now maps `unique<T>` to `std::unique_ptr<T>`.
  - prelude uses `#if __has_include(<memory>)` to prefer real `<memory>` when available and provides a minimal internal `std::unique_ptr` fallback when it is not.
  - template/include cNxt restrictions were tightened to still reject user-source forms while allowing compiler-prelude and system-header processing needed for internal lowering.
  - added parser coverage in `clang/test/Parser/cnxt-unique-lowering.cpp` and updated prelude coverage in `clang/test/Preprocessor/cnxt-prelude.c`.
- What is now unblocked:
  - M3-05 and M3-06 can mirror this pattern for `shared<T>` and `weak<T>`.
  - M3-07 can build on `unique<T>` now being represented as `std::unique_ptr` at the language boundary.
- Direction check:
  - roadmap remains directionally correct; `unique<T>` now has a concrete std-oriented lowering path while preserving no-header requirements for user source.

### 2026-03-15 - M3-05

- Completed item: lower `shared<T>` to an internal std-backed representation.
- What changed:
  - cNxt prelude now maps `shared<T>` to `std::shared_ptr<T>`.
  - internal fallback path now provides a minimal `std::shared_ptr` shape when `<memory>` is unavailable.
  - added parser coverage in `clang/test/Parser/cnxt-shared-lowering.cpp` and updated prelude coverage in `clang/test/Preprocessor/cnxt-prelude.c`.
- What is now unblocked:
  - M3-06 can align `weak<T>` to the same std-backed/fallback prelude strategy.
  - M3-08 can enforce `shared<T>` copy/reference-count semantics on top of the stabilized representation.
- Direction check:
  - roadmap remains directionally correct; both `unique<T>` and `shared<T>` now lower through the same compiler-owned std-oriented prelude boundary.

### 2026-03-15 - M3-06

- Completed item: lower `weak<T>` to an internal std-backed representation.
- What changed:
  - cNxt prelude now maps `weak<T>` to `std::weak_ptr<T>`.
  - internal fallback path now provides a minimal `std::weak_ptr` shape with `lock()` and `expired()` when `<memory>` is unavailable.
  - added parser coverage in `clang/test/Parser/cnxt-weak-lowering.cpp` and updated prelude coverage in `clang/test/Preprocessor/cnxt-prelude.c`.
- What is now unblocked:
  - M3-07/M3-08/M3-09 can now enforce ownership semantics on top of a complete `unique/shared/weak` lowered surface.
- Direction check:
  - roadmap remains directionally correct; all three ownership handle spellings now flow through the same compiler-owned std-oriented lowering boundary.

### 2026-03-15 - M3-07

- Completed item: enforce move-only semantics for `unique<T>`.
- What changed:
  - fallback `std::unique_ptr` in the cNxt prelude now explicitly deletes copy construction/assignment and permits moves.
  - cNxt operator-overload restriction now remains enforced for user code while exempting system-header declarations needed by compiler/runtime-provided ownership internals.
  - added parser/semantic coverage in `clang/test/Parser/cnxt-unique-move-only.cpp`.
- What is now unblocked:
  - M3-08 can focus on `shared<T>` copy/reference semantics without ambiguity around unique ownership copying.
  - M3-09 can rely on a distinct move-only `unique<T>` source when validating weak upgrade/deref rules.
- Direction check:
  - roadmap remains directionally correct; unique ownership now has explicit non-copyable semantics in no-`<memory>` fallback builds while preserving the restricted user surface.

### 2026-03-15 - M3-08

- Completed item: enforce reference-count semantics and copy rules for `shared<T>`.
- What changed:
  - fallback `std::shared_ptr` in the cNxt prelude now has explicit copy/move special member behavior declarations (copyable by design).
  - added parser/semantic coverage in `clang/test/Parser/cnxt-shared-copy-rules.cpp`.
- What is now unblocked:
  - M3-09 can enforce weak upgrade/deref behavior against a stable, explicitly copyable shared-handle surface.
  - M3-10 can add ownership-conversion diagnostics with clearer baseline handle copy/move rules.
- Direction check:
  - roadmap remains directionally correct; shared ownership copy semantics are now explicit in fallback builds while std-backed behavior remains primary when `<memory>` is present.

### 2026-03-15 - M3-09

- Completed item: enforce weak-handle lock-before-use access rules.
- What changed:
  - fallback `std::weak_ptr` in the cNxt prelude now hides raw storage and exposes lock/expired accessors, reducing direct raw-handle access.
  - added parser/semantic coverage in `clang/test/Parser/cnxt-weak-lock-required.cpp` to require lock-style access.
- What is now unblocked:
  - M3-10 can add explicit ownership-conversion diagnostics on top of stable unique/shared/weak access patterns.
  - M3-12 baseline ownership behavior tests can rely on lock-before-use regression coverage.
- Direction check:
  - roadmap remains directionally correct; weak-handle usage now emphasizes lock/upgrade access paths across both std-backed and fallback representations.

### 2026-03-15 - M3-10

- Completed item: add diagnostics for illegal ownership conversions in cNxt assignment flows.
- What changed:
  - added a dedicated cNxt Sema diagnostic for illegal ownership-handle conversion direction (`unique -> shared -> weak` is the only widening path).
  - added ownership-kind classification and conversion-flow checks in semantic assignment handling, including overloaded assignment paths, so rejected flows report cNxt-specific diagnostics instead of generic overload failures.
  - extended cNxt parser/semantic coverage in `clang/test/Parser/cnxt-ownership-conversions.cpp`.
- What is now unblocked:
  - M3-11 can focus on unsafe FFI raw-pointer boundary rules without ambiguity in ownership-handle conversion diagnostics.
  - M3-12 baseline ownership test expansion can now assert explicit illegal-conversion diagnostics.
- Direction check:
  - roadmap remains directionally correct; ownership-handle semantics now expose explicit language-level diagnostics for illegal conversion direction.

### 2026-03-15 - M3-11

- Completed item: add raw-pointer FFI boundary rules for cNxt.
- What changed:
  - semantic declaration checks now reject raw pointer declarations in cNxt user code for variables and fields.
  - cNxt function declarations now reject raw pointer signatures unless the declaration is `extern "C"` (FFI boundary).
  - added parser/semantic coverage in `clang/test/Parser/cnxt-ffi-raw-pointers.cpp` for rejected global/local/field/function-pointer forms and accepted `extern "C"` pointer signatures.
- What is now unblocked:
  - M3-12 can consolidate ownership baseline tests with explicit raw-pointer boundary enforcement coverage.
  - M3-13 interoperability tests can assume explicit `extern "C"` pointer-boundary behavior in cNxt mode.
- Direction check:
  - roadmap remains directionally correct; cNxt now enforces a concrete raw-pointer policy tied to explicit FFI boundaries.

### 2026-03-15 - M3-12

- Completed item: add parser/sema/codegen baseline ownership tests.
- What changed:
  - added parser baseline coverage in `clang/test/Parser/cnxt-ownership-baseline.cpp` for accepted ownership-handle surface operations.
  - added sema baseline coverage in `clang/test/SemaCXX/cnxt-ownership-baseline.cpp` for illegal ownership conversion diagnostics and weak-lock flow typing.
  - added codegen baseline coverage in `clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp` to verify std-backed ownership handle lowering and weak lock/expired call emission in LLVM IR.
- What is now unblocked:
  - M3-13 can focus on mixed cNxt/C++ ABI interoperability with baseline parser/sema/codegen ownership regressions already covered.
- Direction check:
  - roadmap remains directionally correct; ownership milestone confidence is now anchored by dedicated parser, sema, and codegen regression tests.

### 2026-03-15 - M3-13

- Completed item: add mixed cNxt/C++ ABI interoperability coverage.
- What changed:
  - added `clang/test/CodeGenCXX/cnxt-ownership-interop.cpp` with split-file cNxt and C++ translation units.
  - verified cNxt-side IR emission for extern-C ownership-handle and raw-pointer boundary functions.
  - verified C++-side IR declarations/calls use ABI-compatible signatures when calling cNxt extern-C entry points.
- What is now unblocked:
  - milestone 3 is complete; milestone 4 package-manager implementation can start on top of a tested ownership baseline and interop boundary.
- Direction check:
  - roadmap remains directionally correct; ownership runtime work now has cross-language ABI coverage in addition to parser/sema/codegen unit regression tests.

### 2026-03-15 - M4-01

- Completed item: define `Cnxt.toml` manifest schema and validation rules.
- What changed:
  - added `cnxt/specs/cnxt-manifest-schema.md` as the schema source-of-truth for manifest versioning, package metadata, dependency specification forms, target declarations, profiles, and workspace metadata.
  - documented explicit validation constraints and baseline diagnostic IDs (`CNXT1001` through `CNXT1008`) for parser/validator implementation in the next deliverables.
  - linked the schema spec from `cnxt/README.md` in the package-layout section.
- What is now unblocked:
  - M4-02 can implement a parser that validates against a concrete key/type/value contract instead of inferred conventions.
  - M4-03 and M4-04 can build on standardized dependency/source/path semantics and error taxonomy.
- Direction check:
  - roadmap remains directionally correct; milestone 4 now has a concrete manifest contract suitable for incremental parser and resolver implementation.

### 2026-03-15 - M4-02

- Completed item: implement manifest parser with structured diagnostics.
- What changed:
  - added `cnxt/tools/manifest_parser.py` with schema-aware `Cnxt.toml` parsing and validation, including structured diagnostics (`CNXT1001` to `CNXT1008`).
  - implemented a Python 3.11 `tomllib` path and a Python 3.8-compatible minimal TOML parser fallback so parser behavior is stable in this repository environment.
  - added unit coverage in `cnxt/tools/tests/test_manifest_parser.py` for valid manifests, missing/unknown keys, manifest-version checks, dependency source constraints, path escape checks, and structured parse errors.
- What is now unblocked:
  - M4-03 can consume validated manifest objects with normalized schema assumptions and deterministic diagnostic IDs.
  - M4-04 can build constraint solving directly on validated dependency specs (`version`, `path`, `git`) without re-implementing schema checks.
- Direction check:
  - roadmap remains directionally correct; milestone 4 now has executable schema enforcement with test-backed diagnostics as a base for graph and solver work.

### 2026-03-15 - M4-03

- Completed item: implement dependency graph construction and cycle diagnostics.
- What changed:
  - added `cnxt/tools/dependency_graph.py` to build local path-dependency graphs from validated manifests.
  - implemented graph diagnostics for manifest-parse failures, missing path-dependency manifests, duplicate package names, and dependency cycles (`CNXT2001`-`CNXT2004`).
  - added unit coverage in `cnxt/tools/tests/test_dependency_graph.py` for acyclic graphs, missing-path diagnostics, duplicate-name diagnostics, and cycle detection.
- What is now unblocked:
  - M4-04 can perform version-constraint solving on top of a resolved graph shape and package identity map.
  - M4-05 lockfile work can target deterministic graph outputs with explicit cycle/missing-node failure behavior.
- Direction check:
  - roadmap remains directionally correct; milestone 4 now has parser + graph foundations with structured diagnostics for topology errors.

### 2026-03-15 - M4-04

- Completed item: implement version constraint solving.
- What changed:
  - added `cnxt/tools/version_solver.py` to solve manifest dependency requirements and emit structured diagnostics (`CNXT3001`-`CNXT3003`).
  - implemented semver requirement parsing/intersection for exact, comparator, caret, and tilde constraints.
  - added unit coverage in `cnxt/tools/tests/test_version_solver.py` for compatible intersections, conflicting constraints, unsupported requirements, local-version mismatch diagnostics, and caret behavior for `0.x.y`.
- What is now unblocked:
  - M4-05 can consume deterministic solved constraints when generating lockfiles.
  - M4-07 package fetching can rely on already-detected version conflicts/invalid constraints before network resolution.
- Direction check:
  - roadmap remains directionally correct; package-manager flow now has parser, graph, and solver layers with test-backed diagnostics.

### 2026-03-15 - M4-05

- Completed item: implement lockfile format and deterministic lockfile generation.
- What changed:
  - added `cnxt/specs/cnxt-lockfile-schema.md` defining `Cnxt.lock` v1 shape and determinism rules.
  - added `cnxt/tools/lockfile_generator.py` with deterministic lockfile generation, rendering, and file writing (`Cnxt.lock` default output).
  - added unit coverage in `cnxt/tools/tests/test_lockfile_generator.py` for deterministic generation, conflict-failure handling, and default output path writing.
  - linked lockfile spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-06 can lay out cache paths using deterministic lockfile package entries.
  - M4-08/M4-09/M4-10 command work can consume lockfile outputs instead of ad hoc resolution state.
- Direction check:
  - roadmap remains directionally correct; package-manager flow now includes a stable lock artifact between solving and fetch/build steps.

### 2026-03-15 - M4-06

- Completed item: implement local cache layout for downloaded packages.
- What changed:
  - added `cnxt/specs/cnxt-cache-layout.md` defining cache root, directory structure, keying rules, and planning behavior.
  - added `cnxt/tools/cache_layout.py` with deterministic cache root/layout computation, directory initialization, and lockfile-driven cache-entry planning for registry and git dependencies.
  - added structured cache diagnostics (`CNXT5001`-`CNXT5003`) for lockfile loading/validation failures.
  - added unit coverage in `cnxt/tools/tests/test_cache_layout.py` for layout initialization, deterministic keying, lockfile entry planning, and invalid lockfile diagnostics.
  - linked cache layout spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-07 fetcher implementation can use stable cache paths/keys instead of inventing storage conventions.
  - M4-08/M4-10 command work can initialize/cache-plan before invoking download/build steps.
- Direction check:
  - roadmap remains directionally correct; package-manager pipeline now has deterministic manifests -> graph -> solver -> lockfile -> cache-layout staging.

### 2026-03-15 - M4-07

- Completed item: implement package fetcher (registry and git source support).
- What changed:
  - added `cnxt/specs/cnxt-fetcher-sources.md` defining baseline registry index format, version selection behavior, and git source handling.
  - added `cnxt/tools/package_fetcher.py` to fetch lockfile dependencies into cache for both `version` and `git` sources.
  - implemented registry index loading + highest-satisfying-version selection and git mirror/checkout flows.
  - added fetch diagnostics (`CNXT6003`-`CNXT6005`) and structured fetch records for fetched/cached outcomes.
  - added unit coverage in `cnxt/tools/tests/test_package_fetcher.py` for registry + git fetch success, missing registry index failure, and cache-hit behavior on repeated fetch.
  - linked fetcher source spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-08 build command can run lockfile+fetch pipeline with concrete cached inputs.
  - M4-09/M4-10 command work can reuse the same fetch stage before compile/test orchestration.
- Direction check:
  - roadmap remains directionally correct; package-manager foundations now include parsing, solving, locking, cache layout, and source fetching.

### 2026-03-15 - M4-08

- Completed item: implement `cnxt build` command.
- What changed:
  - added `cnxt/tools/cnxt_build.py` to orchestrate manifest validation, lockfile generation, optional dependency fetch, target derivation, compile-command emission, and compile/link execution.
  - implemented `debug`/`release` profile flags and default target discovery (`src/main.cn`, `src/lib.cn`) with explicit `[targets]` support.
  - emits deterministic `compile_commands.json` for derived compile steps.
  - added build diagnostics (`CNXT7001`-`CNXT7004`) for lock/target/command failure scenarios.
  - added `cnxt/specs/cnxt-build-command.md` documenting baseline workflow and diagnostics.
  - added unit coverage in `cnxt/tools/tests/test_cnxt_build.py` for dry-run planning, missing-target failure, and executable build path with a mock compiler.
  - linked build-command spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-09 can reuse build orchestration to run built binaries.
  - M4-10 can reuse build orchestration for test target execution.
- Direction check:
  - roadmap remains directionally correct; package-manager implementation now has a concrete build entry point on top of lock+fetch primitives.

### 2026-03-15 - M4-09

- Completed item: implement `cnxt run` command.
- What changed:
  - added `cnxt/tools/cnxt_run.py` to build-or-reuse artifacts, select binary targets, execute binaries, and return structured run outputs.
  - implemented `--skip-build`, `--bin`, profile selection, and argument forwarding support.
  - added run diagnostics (`CNXT7101`-`CNXT7104`) for binary selection and runtime-failure paths.
  - added `cnxt/specs/cnxt-run-command.md` documenting baseline run workflow and diagnostics.
  - added unit coverage in `cnxt/tools/tests/test_cnxt_run.py` for build+run integration, missing binary handling, and named-binary selection behavior.
  - linked run-command spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-10 can reuse build and runtime execution paths to implement test command behavior.
  - M4-11 workspace discovery can be integrated once run/test command entry points are stable.
- Direction check:
  - roadmap remains directionally correct; command surface now includes build and run baselines backed by lock/fetch/cache plumbing.

### 2026-03-15 - M4-10

- Completed item: implement `cnxt test` command.
- What changed:
  - added `cnxt/tools/cnxt_test.py` to build-or-reuse test artifacts and execute test binaries with structured per-test results.
  - implemented test filtering, skip-build mode, and build/fetch integration via existing command pipeline.
  - added test diagnostics (`CNXT7201`-`CNXT7203`) for no-tests, missing binaries, and failing test executions.
  - added `cnxt/specs/cnxt-test-command.md` documenting baseline `cnxt test` behavior.
  - added unit coverage in `cnxt/tools/tests/test_cnxt_test.py` for pass/fail/no-test scenarios.
  - linked test-command spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-11 workspace/project-root discovery can now be wired across build/run/test command entry points.
  - M4-12 and M4-13 E2E command tests can target stable build/run/test command surfaces.
- Direction check:
  - roadmap remains directionally correct; milestone 4 now has baseline command coverage for build/run/test on top of lock/fetch/cache foundations.

### 2026-03-15 - M4-11

- Completed item: implement workspace/project-root discovery behavior.
- What changed:
  - added `cnxt/tools/workspace_discovery.py` with upward manifest search, workspace-root/member resolution, and structured discovery diagnostics (`CNXT8001`, `CNXT8002`).
  - integrated discovery into `cnxt_build.py`, `cnxt_run.py`, and `cnxt_test.py` so commands accept manifest files, project directories, or current-directory defaults.
  - added `cnxt/specs/cnxt-workspace-discovery.md` documenting resolution rules and command integration.
  - added unit coverage in `cnxt/tools/tests/test_workspace_discovery.py` for workspace-member resolution, missing-manifest errors, and command integration from directory input.
  - linked workspace discovery spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-12 and M4-13 end-to-end test suites can now exercise command flows from workspace/member working directories.
  - M4-14 reproducibility testing can run through stable command entry-point resolution logic.
- Direction check:
  - roadmap remains directionally correct; milestone 4 command ergonomics now include explicit project/workspace discovery behavior.

### 2026-03-15 - M4-12

- Completed item: add end-to-end tests for local path dependencies.
- What changed:
  - added `cnxt/tools/tests/test_e2e_local_path_dependencies.py` covering integrated local path dependency flows.
  - test coverage now exercises build/run/test command pipeline over local path package graphs, including lockfile generation and directory-input command invocation.
  - E2E fixtures include workspace/member layouts and local path dependency manifests validated through command execution with mock compiler outputs.
- What is now unblocked:
  - M4-13 registry E2E tests can reuse the same end-to-end harness structure for non-local sources.
  - M4-14 reproducibility checks can build on existing E2E command scaffolding.
- Direction check:
  - roadmap remains directionally correct; local path dependency behavior is now covered with command-level integration tests rather than only unit slices.

### 2026-03-15 - M4-13

- Completed item: add end-to-end tests for registry dependencies.
- What changed:
  - added `cnxt/tools/tests/test_e2e_registry_dependencies.py` for registry-backed command-level integration coverage.
  - E2E tests now validate build/run/test pipeline behavior with registry dependency resolution and cache population.
  - added negative-path coverage where unsatisfied registry requirements fail builds with the expected diagnostic flow.
- What is now unblocked:
  - M4-14 reproducibility tests can now reuse both local-path and registry E2E fixtures.
  - milestone 4 closure work can focus on deterministic replay guarantees rather than missing source-mode coverage.
- Direction check:
  - roadmap remains directionally correct; milestone 4 now has end-to-end coverage for both local path and registry dependency modes.

### 2026-03-15 - M4-14

- Completed item: add reproducibility tests for lockfile replay in CI.
- What changed:
  - added lock replay E2E coverage in `cnxt/tools/tests/test_e2e_lockfile_replay.py` validating deterministic locked rebuilds.
  - build pipeline now supports `--locked`/locked mode to replay existing lockfiles without regeneration.
  - fetch pipeline now honors lockfile `resolved-version` pins for version-source dependencies.
  - build pipeline persists fetched resolved versions back into lockfile dependency entries to enable deterministic replay.
  - updated lockfile/build/fetch specs to document pinned-version replay behavior and locked build diagnostics.
- What is now unblocked:
  - milestone 4 is complete; milestone 5 IDE-quality deliverables can proceed on top of a test-backed package-manager command pipeline.
- Direction check:
  - roadmap remains directionally correct; package-manager foundation now includes deterministic lockfile replay guarantees suitable for CI reproducibility checks.
