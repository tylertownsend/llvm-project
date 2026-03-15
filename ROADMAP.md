# ROADMAP

Source plan: `cnxt/docs/commit-plan.md`.

## Priority Queue

1. M3-01 Standardize cNxt docs on `unique/shared/weak` ownership vocabulary.
2. M3-02 Parse and type-check `unique<T>`, `shared<T>`, and `weak<T>`.
3. M3-03 Add compiler-owned prelude/injected declarations for ownership handles.

## Deliverable Status

- [x] M1-01 through M1-12
- [x] M2-01 through M2-14
- [x] M3-00
- [ ] M3-01 through M3-13
- [ ] M4-01 through M4-14
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
