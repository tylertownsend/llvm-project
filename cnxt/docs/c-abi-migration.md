# Migrating Manual `extern "C"` Patterns to Compiler-Managed cNxt Interop

Status: Milestone 9 migration guide.

This guide explains when to replace older hand-written C ABI patterns with
`cnxt_import_c` / `cnxt_export_c`, and when to keep `unsafe extern "C"`.

## Why Migrate

The compiler-managed C ABI surface exists to remove wrapper code that adds no
real semantics:

- `cnxt_import_c` imports an unmangled C symbol on a free-function declaration
- `cnxt_export_c` exports a free function under an unmangled C symbol name
- ownership-handle signatures stay in ownership-handle form instead of being
  rewritten into raw-pointer adapters

Use these spellings when the boundary should stay in cNxt value or ownership
terms. Keep `unsafe extern "C"` only for true raw-pointer FFI.

## Decision Rule

Choose the boundary based on what crosses it:

- `cnxt_import_c`: import a C or C++ `extern "C"` symbol when the cNxt side
  should call it directly without a wrapper body
- `cnxt_export_c`: export a cNxt free function directly as an unmangled C
  symbol when no raw-pointer adapter is required
- `unsafe extern "C"`: keep this spelling when the boundary exchanges raw
  pointers, pointer-derived lifetimes, or other manually audited contracts

## Common Migrations

### 1. Importing a Scalar C Symbol

Legacy pattern:

```cpp
extern "C" int c_increment(int value);

int next(int value) {
  return c_increment(value);
}
```

Preferred pattern:

```cpp
cnxt_import_c int c_increment(int value);

int next(int value) {
  return c_increment(value);
}
```

Why:

- the imported symbol is still the same unmangled C symbol
- the source now says this is a compiler-managed interop edge rather than an
  ad hoc linkage spelling

### 2. Exporting a cNxt Function Without a Wrapper

Legacy pattern:

```cpp
int next(int value) {
  return value + 1;
}

extern "C" int next_c(int value) {
  return next(value);
}
```

Preferred pattern:

```cpp
cnxt_export_c int next(int value) {
  return value + 1;
}
```

Why:

- the wrapper body disappears
- the exported function remains the real implementation
- diagnostics and future tooling can treat this as a dedicated interop surface

Current limitation:

- `cnxt_export_c` exports the function under its own identifier
- if the legacy wrapper intentionally changed the public symbol name, keep the
  wrapper until the compiler grows first-class symbol-renaming control

### 3. Migrating Ownership-Handle Boundaries

Legacy pattern:

```cpp
extern "C" shared<int> cnxt_lock(weak<int> weak_handle) {
  return weak_handle.lock();
}
```

Preferred pattern:

```cpp
cnxt_export_c shared<int> cnxt_lock(weak<int> weak_handle) {
  return weak_handle.lock();
}
```

And for imports:

```cpp
cnxt_import_c shared<int> cnxt_lock(weak<int> weak_handle);
```

Why:

- the compiler-managed surface preserves the ownership-handle ABI
- the source stays in `unique/shared/weak` vocabulary
- callers do not need wrapper code that converts handles into raw pointers

Important:

- this surface is for cNxt-aware peers, typically cNxt or C++ code that agrees
  on the handle layout/contract
- plain C code still cannot author `unique<T>`, `shared<T>`, or `weak<T>`

### 4. Raw-Pointer APIs Do Not Migrate

Keep this form:

```cpp
unsafe extern "C" int *borrow(Buffer *buffer);
```

Do not rewrite raw-pointer boundaries to `cnxt_import_c` / `cnxt_export_c`.
Those spellings are for compiler-managed value and ownership surfaces, not for
manual pointer contracts.

If older code still uses plain `extern "C"` with raw pointers, the current
compiler diagnostics intentionally push it to `unsafe extern "C"`.

## Migration Checklist

1. Inventory each manual `extern "C"` declaration or wrapper.
2. Classify the boundary:
   value/ownership surface or raw-pointer surface.
3. Replace value/ownership imports with `cnxt_import_c`.
4. Replace wrapper-style exports with `cnxt_export_c` when the symbol name can
   match the function identifier.
5. Keep raw-pointer boundaries under `unsafe extern "C"`.
6. Re-run interop coverage after each conversion.

## Verified Coverage in This Branch

- `clang/test/Driver/cnxt-c-abi-mixed-interop.c`
  proves end-to-end cNxt <-> C/C++ calls through compiler-managed C ABI
  imports and exports.
- `clang/test/CodeGenCXX/cnxt-c-abi-ownership-marshalling.cpp`
  locks in ownership-handle marshalling rules across the compiler-managed C
  symbol surface.
- `clang/test/SemaCXX/cnxt-c-abi-pointer-guidance.cpp`
  locks in diagnostics that keep raw-pointer FFI on `unsafe extern "C"`.

## Practical Rule of Thumb

If the boundary can stay in cNxt value or ownership terms, use the
compiler-managed spellings.

If the boundary fundamentally speaks in addresses, buffers, or borrowed raw
storage, keep `unsafe extern "C"` and treat it as a manual audit point.
