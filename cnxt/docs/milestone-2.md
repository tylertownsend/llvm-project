# cNxt Milestone 2

## Goal

Milestone 2 starts enforcing the cNxt language shape while still using
Clang's C++ parser and AST as the host implementation.

This milestone is about narrowing the accepted surface area quickly and
deliberately. It is not yet the phase where cNxt-native keywords like `fn`,
`match`, `defer`, or `for item in expr` get first-class syntax.

## Why this milestone exists

Milestone 1 gave cNxt a stable identity in the driver, frontend, tooling, and
clangd. The next risk is that cNxt still behaves like "mostly C++" unless the
compiler actively rejects the constructs that the language design removes.

Milestone 2 starts turning the language mode into a real dialect by:

- keeping the existing parser and semantic pipeline
- rejecting unsupported C++ constructs with direct cNxt diagnostics
- preserving parser recovery so tooling and future milestones stay practical

## Scope

### In scope

- parse cNxt as a restricted C++-derived language
- emit cNxt-specific diagnostics for unsupported constructs
- keep range-based `for` working as the single supported `for` form for now
- add parser coverage for the first wave of banned constructs

### Out of scope

- introducing `fn`, `match`, `defer`, or `for item in expr`
- lowering ownership handles like `unique<T>` or `shared<T>`
- package manager work
- module/package source layout enforcement
- formatter or linter work

## Initial enforcement slice

The first slice of Milestone 2 should reject these constructs in cNxt mode:

- `goto`
- `do/while`
- C-style `for (...)`
- `try` / `catch`
- `throw`
- `new` / `delete`

This lines up with the v1 language model:

- only one loop surface form should survive
- exceptions are out of scope
- heap ownership should not be expressed with raw C++ allocation syntax

## Implementation approach

Use parser entry points that already correspond to the banned syntax and emit
hard cNxt diagnostics there. Do not fork the parser into a cNxt-only frontend
yet.

Guidelines:

- prefer localized hooks in `ParseStmt.cpp` and `ParseExprCXX.cpp`
- keep parsing and AST construction alive after the diagnostic so recovery
  remains good
- use `LangOptions` feature bits to gate restrictions:
  - `CNxtSingleLoopForms`
  - `CNxtNoExceptions`
  - `CNxtManagedMemory`

## Acceptance criteria

Milestone 2 has started successfully when all of the following are true:

1. `-x cnxt -std=cnxt1` still selects cNxt mode correctly.
2. A range-based `for` still parses in cNxt mode.
3. `goto`, `do/while`, C-style `for`, `try`, `throw`, `new`, and `delete`
   produce direct cNxt errors.
4. Existing Milestone 1 driver/frontend/clangd tests still pass.

## Follow-on work

After this first restriction slice, the next practical bans are:

- templates and template declarations
- inheritance and base-specifier lists
- operator overloading
- C-style casts outside explicit `unsafe` regions
- macros and textual includes in user-facing cNxt package flows
