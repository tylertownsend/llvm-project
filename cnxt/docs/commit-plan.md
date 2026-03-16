# cNxt Commit Plan

This plan breaks the roadmap into small, reviewable, commit-sized deliverables.
Each line item should ship with targeted tests.

## Dependency Order

1. Milestone 1: language mode and driver plumbing (foundation)
2. Milestone 2: restricted subset enforcement
3. Milestone 3: ownership runtime and language-level handles
4. Milestone 4: package manager and project workflows
5. Milestone 5: IDE quality and guardrail tooling

## Milestone 1 Deliverables (Language Identity)

- [x] M1-01 Add `Language::CNxt` and language-to-string support.
- [x] M1-02 Register `lang_cnxt1` / `-std=cnxt1`.
- [x] M1-03 Select `cnxt1` as the default standard for cNxt inputs.
- [x] M1-04 Add cNxt `LangOptions` feature bits and defaults.
- [x] M1-05 Add `-x cnxt` frontend parsing and command-line round-trip.
- [x] M1-06 Add driver types for cNxt source and preprocessed cNxt source.
- [x] M1-07 Map `.cn`, `.cnxt`, and `.cni` in driver/ frontend extension lookup.
- [x] M1-08 Wire cNxt language detection through `ASTUnit` / `CompilerInstance`.
- [x] M1-09 Preserve cNxt type in interpolated compile database logic.
- [x] M1-10 Classify `.cn` / `.cnxt` correctly in clangd source heuristics.
- [x] M1-11 Add driver tests for extension mapping and `-x/-std` behavior.
- [x] M1-12 Add frontend/unit tests for standard compatibility and invocation.

## Milestone 2 Deliverables (Restricted Subset Compiler)

- [x] M2-01 Add parser diagnostics for unsupported cNxt features.
- [x] M2-02 Reject `goto` in cNxt mode.
- [x] M2-03 Reject `do/while` in cNxt mode.
- [x] M2-04 Reject C-style `for (...)` and keep range-for as the only `for`.
- [x] M2-05 Reject `try/catch` in cNxt mode.
- [x] M2-06 Reject `throw` expressions in cNxt mode.
- [x] M2-07 Reject `new` / `delete` expressions in cNxt mode.
- [x] M2-08 Add parser coverage for the first enforcement slice.
- [x] M2-09 Reject template declarations and explicit/implicit template use.
- [x] M2-10 Reject inheritance and base-specifier syntax.
- [x] M2-11 Reject operator overloading declarations.
- [x] M2-12 Restrict C-style casts to explicit `unsafe` regions only.
- [x] M2-13 Reject textual include-based cNxt package flows (policy diagnostic).
- [x] M2-14 Add recovery-focused tests for each new restriction.

## Milestone 3 Deliverables (Ownership Runtime)

Decision for this milestone:
- cNxt surface vocabulary uses `unique<T>`, `shared<T>`, and `weak<T>`.
- These are language-level handles in cNxt source (no required `#include <memory>`).
- Backend lowering should reuse C++ memory machinery where feasible (for example,
  `std::unique_ptr`, `std::shared_ptr`, `std::weak_ptr`) behind the language surface.

- [x] M3-00 Feasibility spike: prove std-backed lowering can work without user
      memory headers and define fallback constraints if not.
- [x] M3-01 Update cNxt docs to standardize ownership vocabulary on
      `unique/shared/weak` (replace prior `strong` wording).
- [x] M3-02 Parse and type-check `unique<T>`, `shared<T>`, and `weak<T>` in cNxt.
- [x] M3-03 Add an implicit cNxt prelude/injected declarations so ownership
      handles are available without explicit memory headers.
- [x] M3-04 Lower `unique<T>` to an internal std-backed representation.
- [x] M3-05 Lower `shared<T>` to an internal std-backed representation.
- [x] M3-06 Lower `weak<T>` to an internal std-backed representation.
- [x] M3-07 Enforce move-only semantics for `unique<T>`.
- [x] M3-08 Enforce reference-count semantics and copy rules for `shared<T>`.
- [x] M3-09 Enforce `weak<T>` access rules (upgrade/lock before dereference).
- [x] M3-10 Add diagnostics for illegal ownership conversions/escapes.
- [x] M3-11 Add FFI boundary rules for raw pointers in `unsafe` code paths.
- [x] M3-12 Add parser/sema/codegen tests for ownership baseline behavior.
- [x] M3-13 Add ABI/interoperability tests with mixed cNxt and C++ compilation.

## Milestone 4 Deliverables (Package Manager)

- [x] M4-01 Define `Cnxt.toml` manifest schema and validation rules.
- [x] M4-02 Implement manifest parser with structured diagnostics.
- [x] M4-03 Implement dependency graph construction and cycle diagnostics.
- [x] M4-04 Implement version constraint solving.
- [x] M4-05 Implement lockfile format and deterministic lockfile generation.
- [x] M4-06 Implement local cache layout for downloaded packages.
- [ ] M4-07 Implement package fetcher (registry and git source support).
- [ ] M4-08 Implement `cnxt build` command.
- [ ] M4-09 Implement `cnxt run` command.
- [ ] M4-10 Implement `cnxt test` command.
- [ ] M4-11 Implement workspace/project-root discovery behavior.
- [ ] M4-12 Add end-to-end tests for local path dependencies.
- [ ] M4-13 Add end-to-end tests for registry dependencies.
- [ ] M4-14 Add reproducibility tests for lockfile replay in CI.

## Milestone 5 Deliverables (IDE Quality)

- [ ] M5-01 Ensure clangd fallback compile commands select cNxt mode.
- [ ] M5-02 Improve completion ranking for cNxt-first constructs and restrictions.
- [ ] M5-03 Add semantic token classification coverage for cNxt files.
- [ ] M5-04 Add go-to-definition/reference regression tests for cNxt sources.
- [ ] M5-05 Add refactor safety checks for restricted constructs.
- [ ] M5-06 Implement cNxt formatter baseline profile.
- [ ] M5-07 Add lints enforcing one-obvious-way language policies.
- [ ] M5-08 Add fix-its for common restriction diagnostics (where safe).
- [ ] M5-09 Add IDE integration tests to CI with representative cNxt projects.

## Suggested Commit Sequencing

1. Finish Milestone 2 pending enforcement items (M2-09 through M2-14).
2. Execute M3-00 first to lock in the std-backed ownership strategy.
3. Land M3-01 through M3-03 before lowering work so syntax and prelude are stable.
4. Land M3-04 through M3-09 one handle/rule at a time with tests.
5. Land M3-10 through M3-13 after semantics settle.
6. Start Milestone 4 only after Milestone 3 ownership tests are green.
7. Land Milestone 5 in small vertical slices tied to concrete clangd/formatter/lint tests.
