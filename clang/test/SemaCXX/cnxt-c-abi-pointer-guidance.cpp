// RUN: not %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -fdiagnostics-parseable-fixits %s 2>&1 | FileCheck %s

cnxt_import_c int *bad_import(int *p);
// CHECK: error: cNxt does not support raw pointer function signatures outside unsafe FFI boundaries
// CHECK: note: 'cnxt_import_c' and 'cnxt_export_c' preserve ownership-handle ABI surfaces; use 'unsafe extern "C"' for raw-pointer FFI
// CHECK: note: for cNxt-owned heap values, prefer 'unique<T>' with 'make<T>(...)'; use 'share(...)' when shared ownership is required
// CHECK: note: use 'unsafe extern "C"' when a raw-pointer FFI boundary is required

cnxt_export_c int *bad_export(int *p) {
  return p;
}
// CHECK: error: cNxt does not support raw pointer function signatures outside unsafe FFI boundaries
// CHECK: note: 'cnxt_import_c' and 'cnxt_export_c' preserve ownership-handle ABI surfaces; use 'unsafe extern "C"' for raw-pointer FFI
// CHECK: note: for cNxt-owned heap values, prefer 'unique<T>' with 'make<T>(...)'; use 'share(...)' when shared ownership is required
// CHECK: note: use 'unsafe extern "C"' when a raw-pointer FFI boundary is required

cnxt_export_c void bad_escape(unique<int> owner) {
  (void)owner.get();
  // CHECK: error: cNxt does not allow ownership handle raw-pointer escape via 'get' outside unsafe FFI boundaries
  // CHECK: note: prefer passing or moving ownership handles directly; use 'share(...)' to widen instead of extracting raw pointers
  // CHECK: note: 'cnxt_import_c' and 'cnxt_export_c' preserve ownership-handle ABI surfaces; use 'unsafe extern "C"' for raw-pointer FFI
  // CHECK: note: use 'unsafe extern "C"' when a raw-pointer FFI boundary is required
}

// CHECK-NOT: fix-it:
