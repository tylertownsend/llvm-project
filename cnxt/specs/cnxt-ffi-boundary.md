# cNxt FFI Boundary Model (`unsafe extern`)

Status: Milestone 9 FFI-boundary baseline.

This document defines where raw pointers are legal in user-authored cNxt code,
why those cases require explicit `unsafe`, and how the current compiler draws
the line between ordinary cNxt code and foreign-function boundaries.

## Goals

- keep ordinary cNxt programs free of raw-pointer syntax and pointer-driven
  lifetime rules
- make raw-pointer-bearing interop sites explicit in the source with a single
  spelling: `unsafe extern "C"`
- align parser/Sema diagnostics and fix-its around one boundary model
- preserve room for later milestones to generate ABI thunks so users need less
  handwritten FFI glue over time

## Non-Goals (M9-01 baseline)

- compiler-generated ABI thunks for ordinary cNxt functions
- automatic marshalling rules for ownership handles across generated thunks
- a complete `ptr<T>` operator/method surface for non-FFI code
- safe stdlib replacements for every common `extern` import

Those items are covered by later Milestone 9 deliverables.

## Terms

- safe code: ordinary cNxt declarations and function bodies that do not opt
  into FFI-unsafety
- raw pointer: C/C++ pointer spelling such as `T *`
- ownership handle escape: extracting a raw pointer from an ownership handle
  using operations such as `unique<T>.get()`, `unique<T>.release()`, or
  `shared<T>.get()`
- FFI boundary: a declaration or definition that intentionally exposes the C
  ABI to exchange values with non-cNxt code

## Boundary Surface

The cNxt baseline recognizes three distinct cases:

### 1. Ordinary cNxt declarations

Raw pointers are not legal in ordinary user declarations.

Rejected examples:

```cpp
int *global_ptr;

struct PointerField {
  int *field;
};

int *not_ffi(int *p);
```

Current compiler behavior:

- raw-pointer globals are rejected
- raw-pointer locals are rejected
- raw-pointer fields are rejected
- raw-pointer function signatures are rejected

This keeps safe cNxt code on value types plus `unique<T>`, `shared<T>`,
`weak<T>`, and later stdlib-owned safe surfaces.

### 2. `extern "C"` without `unsafe`

Plain `extern "C"` is legal only when the surface remains raw-pointer-free.

Example:

```cpp
extern "C" shared<int> cnxt_lock(weak<int> weak_handle) {
  return weak_handle.lock();
}
```

Meaning:

- the ABI is C-compatible
- the declaration is still treated as part of the safe cNxt surface
- raw pointers do not become legal merely because the ABI spelling is
  `extern "C"`

Therefore, this is still rejected:

```cpp
extern "C" int *echo(int *p);
```

The compiler diagnoses that signature and suggests `unsafe extern "C"` when a
raw-pointer boundary is actually intended.

### 3. `unsafe extern "C"`

`unsafe extern "C"` is the only user-authored source spelling that makes
raw-pointer-bearing function signatures legal in cNxt.

Example:

```cpp
unsafe extern "C" int *cnxt_echo_ptr(int *p) {
  return p;
}
```

This form means all of the following at once:

- `extern "C"`: use the C ABI surface
- `unsafe`: the boundary may expose raw addresses or other operations whose
  safety/lifetime cannot be proven by normal cNxt rules

## What Is Legal Inside `unsafe extern "C"`

The current compiler baseline allows these FFI-only escape hatches inside an
`unsafe extern "C"` function:

- raw pointer parameters
- raw pointer return types
- ownership-handle raw escapes:
  - `unique<T>.get()`
  - `unique<T>.release()`
  - `shared<T>.get()`

Example:

```cpp
unsafe extern "C" void allow_ffi_handle_escapes(unique<int> unique_owner,
                                                 shared<int> shared_owner) {
  (void)unique_owner.get();
  (void)unique_owner.release();
  (void)shared_owner.get();
}
```

Rationale:

- foreign code often requires an address-based API
- cNxt ownership semantics cannot prove the foreign side will honor lifetime,
  aliasing, or mutability expectations
- requiring `unsafe` makes that audit boundary explicit in code review and in
  diagnostics

## What Remains Illegal Even With `unsafe extern "C"`

The current baseline is intentionally narrower than "all raw pointer usage is
allowed in unsafe code".

Still rejected in user-authored cNxt source:

- raw-pointer global declarations
- raw-pointer local declarations
- raw-pointer stored fields
- ordinary non-FFI helper functions with raw-pointer signatures

In other words, `unsafe extern "C"` legalizes raw-pointer exchange at function
boundaries, not arbitrary pointer-oriented programming throughout cNxt code.

## Why This Model Exists

The rule is intentionally asymmetric:

- ordinary cNxt code should express ownership through `unique/shared/weak`
- foreign ABIs often speak only in raw addresses and C layout rules
- the compiler can safely optimize and diagnose cNxt code only while ownership
  remains explicit
- once execution crosses into raw-pointer FFI, ownership and aliasing become a
  manual contract, so the source must say `unsafe`

This is why plain `extern "C"` is insufficient: ABI choice alone does not mean
the programmer has acknowledged lifetime unsafety.

## Diagnostics Contract

When users violate the boundary model, the compiler should:

- reject raw-pointer declarations outside the FFI boundary
- reject raw-pointer function signatures unless they are spelled
  `unsafe extern "C"`
- reject ownership-handle raw-pointer escapes outside `unsafe extern "C"`
- emit cNxt-specific guidance:
  - prefer `unique<T>` with `make<T>(...)` for owned heap values
  - prefer `share(...)` when widening ownership is required
  - suggest inserting `unsafe ` before `extern "C"` when the user is clearly
    defining a raw-pointer FFI edge

## Relationship to Later Milestones

This document defines the manual boundary that exists today. Later milestones
should reduce how often users need to write it directly:

- M9-02 adds safe stdlib entrypoints so common app code needs fewer imports
- M9-03 adds compiler-generated ABI thunks
- M9-04 defines handle marshalling rules across those thunks
- M9-05 aligns linting/diagnostics with this boundary as the enforced policy
- M9-07 documents migration away from ad hoc manual `extern "C"` patterns in
  `cnxt/docs/c-abi-migration.md`

## Ownership-Handle Marshalling Across Compiler-Managed C Symbols

Milestones M9-03 and M9-04 add a compiler-managed symbol surface for free
functions:

- `cnxt_export_c` on a definition exports the function under an unmangled C
  symbol name
- `cnxt_import_c` on a declaration imports that same unmangled C symbol name

This surface does not turn ownership handles into raw pointers. Instead, the
compiler preserves the ownership-handle ABI that cNxt already uses for
`unique<T>`, `shared<T>`, and `weak<T>`.

### Marshalling Contract

- `unique<T>` crosses the boundary as an owned move-only handle value:
  - exporting `cnxt_export_c unique<T> f(unique<T>)` keeps the cNxt ownership
    surface at the boundary; no raw-pointer shim is introduced.
  - importing `cnxt_import_c unique<T> g(unique<T>)` lowers a call as a move of
    the caller's handle into the ABI call, and the callee becomes responsible
    for the received ownership.
- `shared<T>` crosses the boundary as a shared-ownership handle value:
  - importing or exporting a `shared<T>` parameter/value preserves reference
    counting semantics.
  - a cNxt caller still performs the same copy/destroy operations it would for
    any other `shared<T>` call site; the compiler-managed symbol name does not
    bypass those rules.
- `weak<T>` crosses the boundary as a weak observer handle value:
  - imported/exported `weak<T>` parameters preserve observer semantics.
  - `lock()` and `expired()` remain runtime-backed operations on the cNxt side
    of the boundary.

### Boundary Shape

- compiler-managed C symbols keep ownership vocabulary in the source signature;
  user code does not write raw-pointer adapters just to pass ownership handles
- the generated symbol name is C-friendly, but the value contract remains the
  cNxt ownership-handle ABI defined by the ownership runtime baseline
- this surface is intended for cNxt-to-cNxt and cNxt-to-C++ interop where both
  sides understand the handle layout/contract
- plain C source still cannot author `unique<T>`, `shared<T>`, or `weak<T>`
  directly; raw-pointer C APIs remain the domain of `unsafe extern "C"`

### Audit Rule

Choose the boundary based on what is being exchanged:

- use `cnxt_export_c` / `cnxt_import_c` when the boundary should remain in
  ownership-handle terms
- use `unsafe extern "C"` when the boundary genuinely needs raw addresses or
  pointer-centric lifetime contracts

The compiler should not silently rewrite ownership-handle signatures into raw
pointer signatures, because that would hide the exact ownership contract the
language is trying to preserve.

## Acceptance Criteria for M9-01

- this spec is the source of truth for where raw pointers are legal in current
  cNxt user code
- the document explains why `unsafe extern "C"` exists as a separate spelling
  from plain `extern "C"`
- later implementation and migration deliverables can build on this policy
  without redefining the safe/unsafe boundary
