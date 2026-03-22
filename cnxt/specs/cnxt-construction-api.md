# cNxt Construction API (`make<T>(...)`)

Status: Milestone 7 construction-surface baseline.

This document defines the intended user-facing heap-construction API for cNxt
safe code. It replaces the temporary Milestone 6 `make_unique(value)` helper as
the long-term source of truth for owned-object construction.

## Goals

- let safe cNxt code allocate heap objects without spelling raw pointers
- return language-owned `unique<T>` handles directly from construction
- hide runtime ABI details such as `__cnxt_rt_own_v1_alloc` from user code
- preserve deterministic destruction through existing `unique<T>` scope-exit
  semantics

## Non-Goals (M7 baseline)

- custom allocator selection or allocator traits
- direct `shared<T>` / `weak<T>` construction from the allocation surface
- placement-style construction into caller-provided storage
- array/slice allocation syntax
- exposing raw pointer construction helpers in safe code

## User-Facing Surface

The construction expression form is:

- `make<T>()`
- `make<T>(arg0, arg1, ..., argN)`

Result type:

- `make<T>(...)` always has type `unique<T>`.

Examples:

```cpp
unique<int> value = make<int>(42);
unique<Point> point = make<Point>(1, 2);
```

## Type Rules

- `T` must name a concrete, complete, non-reference object type.
- `T` must not be a raw pointer type.
- `T` must not be an ownership handle type (`unique<U>`, `shared<U>`,
  `weak<U>`); construction operates on payload types, not on handles.
- `make<T>(...)` is valid only when `T` can be initialized from the provided
  argument list under cNxt initialization rules.
- Construction never implicitly widens to `shared<T>` or `weak<T>`. The
  construction API yields `unique<T>` first; widening remains an explicit
  follow-up operation.

## Safety Rules

- `make<T>(...)` is the safe-code heap allocation surface for ordinary cNxt
  programs.
- User code must not need to declare or call runtime ABI entry points directly
  in order to construct owned heap values.
- User code must not need to declare raw pointer locals to allocate a value.
- `new`, `delete`, and raw-pointer-returning allocation APIs remain rejected in
  safe cNxt code.

## Initialization Semantics

- `make<T>()` value-initializes the payload value.
- `make<T>(arg0, ..., argN)` initializes the payload from the supplied
  arguments using the same constructor/initializer selection rules that cNxt
  will define for ordinary value initialization.
- Argument evaluation is left-to-right.
- If initialization of `T` is ill-formed for the provided arguments, the
  program is rejected at compile time with a cNxt-specific diagnostic.

## Ownership Semantics

- The storage returned by `make<T>(...)` is owned exclusively by the resulting
  `unique<T>`.
- Scope exit, reassignment, and explicit reset follow the existing `unique<T>`
  destruction rules.
- If the resulting `unique<T>` is moved, ownership transfers exactly once.
- If the result needs shared ownership, the program must perform an explicit
  ownership-widening step (`share(unique<T>) -> shared<T>`) after construction
  rather than constructing `shared<T>` directly.

## Runtime / Lowering Contract

- `make<T>(...)` lowers to:
  1. runtime allocation via the compiler-owned ownership runtime ABI
  2. initialization of the payload object in the allocated storage
  3. wrapping the payload in a `unique<T>` handle
- The allocation path inherits Milestone 6 runtime behavior:
  - OOM terminates or traps according to the runtime ABI contract
  - destruction routes through compiler-managed `unique<T>` cleanup
- No user-authored `extern "C"` declarations are part of the construction API
  contract.

## Diagnostics Expectations

- Direct raw-pointer-based heap construction in safe code should diagnose and
  point users at `make<T>(...)` once the implementation lands.
- `make<T>(...)` with an incomplete type, ownership-handle payload, or invalid
  argument list should fail with cNxt-specific diagnostics.
- Fix-its may rewrite transitional `make_unique(value)` spellings to
  `make<T>(...)` when the type is known and such a rewrite is
  semantics-preserving.

## Transition from Milestone 6 Helper

- The injected `make_unique(value)` helper added in Milestone 6 is a temporary
  bridge so the branch can demonstrate a no-`extern "C"` ownership example
  before the full construction surface is implemented.
- `make_unique(value)` is not the committed long-term language API.
- Milestone 7 implementation work should converge user code on `make<T>(...)`
  and remove or demote the temporary helper once parser, sema, and codegen
  support are in place.

## Acceptance Criteria for M7-01

- This spec is the source of truth for the user-facing construction API.
- The spec makes raw-pointer-free construction the intended safe-code path.
- Follow-on implementation milestones can derive parser, sema, codegen, and
  diagnostics behavior directly from this document.
