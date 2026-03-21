# cNxt Ownership Runtime ABI (`libcnxt_ownership_rt`)

Status: Milestone 6 ownership-runtime baseline (`abi-version = 1`).

This document defines the compiler/runtime ABI contract for cNxt ownership
handles:

- `unique<T>`
- `shared<T>`
- `weak<T>`

The contract is intentionally C ABI based so compiler-generated calls are
stable across C++ standard library implementations and do not require user
source to include host C++ memory headers.

## Goals

- remove user-facing dependence on host `<memory>` parsing in cNxt mode
- provide one compiler-owned ABI for allocation and ownership transitions
- keep normal cNxt code free of manual `extern "C"` ownership glue
- make ownership behavior testable at parser/sema/codegen/runtime levels

## Non-Goals (v1 ABI)

- user-defined allocator plugins
- cross-process shared ownership
- cycle collection / tracing GC
- stable C++ API surface; this is a C ABI only contract

## ABI Principles

- All exported symbols use C linkage.
- All exported symbols for ABI v1 are prefixed:
  `__cnxt_rt_own_v1_`.
- Runtime calls must not throw C++ exceptions across ABI boundaries.
- Shared/weak reference counting must be thread-safe.
- ABI v1 changes are additive only. Breaking changes require ABI v2 symbols.

## Runtime Handle Model

Compiler lowering uses two opaque runtime concepts:

- `object` pointer: `void *` to user payload (`T` instance memory)
- `control` pointer: `void *` to runtime-owned shared/weak control block

`unique<T>` is represented as an owning object pointer with compiler-known
drop metadata (destructor + layout). `shared<T>` and `weak<T>` are represented
by control pointers.

## Required Exported Symbols (ABI v1)

### ABI/version

- `uint32_t __cnxt_rt_own_v1_abi_version(void);`
  - Must return `1`.

### Unique ownership and allocation

- `void *__cnxt_rt_own_v1_alloc(uint64_t size, uint64_t align);`
  - Allocates payload storage.
  - Runtime must terminate or trap on OOM; call does not return null.
- `void __cnxt_rt_own_v1_unique_drop(void *object, void (*dtor)(void *), uint64_t size, uint64_t align);`
  - Drops a `unique<T>` payload.
  - If `dtor` is non-null, runtime calls it before deallocation.
  - Accepts null `object` as no-op.

### Shared ownership

- `void *__cnxt_rt_own_v1_shared_from_unique(void *object, void (*dtor)(void *), uint64_t size, uint64_t align);`
  - Consumes unique-owned payload and returns a new control pointer with strong
    count initialized to 1 and weak count initialized per runtime policy.
- `void __cnxt_rt_own_v1_shared_retain(void *control);`
  - Increments strong count; null is no-op.
- `void __cnxt_rt_own_v1_shared_release(void *control);`
  - Decrements strong count.
  - When strong count reaches zero, runtime drops/deallocates payload and
    eventually frees the control block when weak count reaches zero.
  - Null is no-op.
- `void *__cnxt_rt_own_v1_shared_get(void *control);`
  - Returns payload pointer for read/write access in codegen lowering.
  - Returns null when control is null or payload already destroyed.

### Weak ownership

- `void __cnxt_rt_own_v1_weak_retain(void *control);`
  - Increments weak count; null is no-op.
- `void __cnxt_rt_own_v1_weak_release(void *control);`
  - Decrements weak count; null is no-op.
- `void *__cnxt_rt_own_v1_weak_lock(void *control);`
  - If payload is alive, increments strong count and returns same control
    pointer as a `shared<T>` handle.
  - Returns null when expired or when control is null.
- `uint8_t __cnxt_rt_own_v1_weak_expired(void *control);`
  - Returns `1` when payload is expired or control is null, else `0`.

## Compiler Lowering Contract

- `unique<T>` creation lowers to:
  `alloc` -> constructor/init -> unique handle.
- Unique scope-exit cleanup lowers to `unique_drop`.
- `unique<T> -> shared<T>` conversion lowers to `shared_from_unique`.
- `shared<T>` copy/move/drop lower to retain/release operations.
- `weak<T>` copy/move/drop lower to weak retain/release operations.
- `weak.lock()` lowers to `weak_lock`; `weak.expired()` lowers to
  `weak_expired`.
- Runtime function declarations emitted by CodeGen must use C calling
  convention and exact ABI v1 symbol names.

## Threading and Memory Ordering

- `shared_retain/shared_release/weak_retain/weak_release/weak_lock` must be
  safe under concurrent access from multiple threads.
- Runtime may choose implementation details (mutex or atomics), but observable
  semantics must match linearizable reference-count updates.

## Diagnostics and Linkage Requirements

- cNxt frontend/driver must diagnose missing ownership runtime linkage with a
  cNxt-specific message.
- If `__cnxt_rt_own_v1_abi_version()` is absent or returns unsupported value,
  compilation or link flow must fail with explicit ABI mismatch diagnostics.

## Symbol Naming and Versioning Policy

- v1 symbols are immutable once released.
- Backward-compatible additions in v1 use new symbols with same
  `__cnxt_rt_own_v1_` prefix.
- Breaking changes require `__cnxt_rt_own_v2_` symbol family and a new
  `abi-version` value.
- Runtime shared object naming convention:
  - `libcnxt_ownership_rt.so.1` for ABI v1.

## Acceptance Criteria for M6 Runtime Baseline

- Spec is the source of truth for ownership runtime ABI v1.
- CodeGen/runtime implementation work references this symbol set directly.
- End-to-end ownership tests can run without user-authored `<memory>` includes
  or manual `extern "C"` ownership wrappers.
