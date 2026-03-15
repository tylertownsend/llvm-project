# ROADMAP

Source plan: `cnxt/docs/commit-plan.md`.

## Priority Queue

1. M2-12 Restrict C-style casts to explicit `unsafe` regions only.
2. M2-13 Reject textual include-based cNxt package flows.
3. M2-14 Add recovery-focused tests for the remaining restrictions.

## Deliverable Status

- [x] M1-01 through M1-12
- [x] M2-01 through M2-11
- [ ] M2-12 through M2-14
- [ ] M3-00 through M3-13
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
