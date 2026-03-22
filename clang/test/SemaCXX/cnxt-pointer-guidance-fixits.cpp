// RUN: not %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -fdiagnostics-parseable-fixits %s 2>&1 | FileCheck %s

int *global_ptr;
// CHECK: error: cNxt does not support raw pointer declarations outside unsafe FFI boundaries
// CHECK: note: for cNxt-owned heap values, prefer 'unique<T>' with 'make<T>(...)'; use 'share(...)' when shared ownership is required

extern "C" int *extern_c_without_unsafe(int *p);
// CHECK: note: for cNxt-owned heap values, prefer 'unique<T>' with 'make<T>(...)'; use 'share(...)' when shared ownership is required
// CHECK: note: use 'unsafe extern "C"' when a raw-pointer FFI boundary is required
// CHECK: error: cNxt does not support raw pointer function signatures outside unsafe FFI boundaries
// CHECK: fix-it:"{{.*}}":{[[@LINE-4]]:1-[[@LINE-4]]:1}:"unsafe "

extern "C" void reject_plain_extern_handle_escapes(unique<int> unique_owner) {
  (void)unique_owner.get();
  // CHECK: note: prefer passing or moving ownership handles directly; use 'share(...)' to widen instead of extracting raw pointers
  // CHECK: note: use 'unsafe extern "C"' when a raw-pointer FFI boundary is required
  // CHECK: error: cNxt does not allow ownership handle raw-pointer escape via 'get' outside unsafe FFI boundaries
  // CHECK: fix-it:"{{.*}}":{[[@LINE-5]]:1-[[@LINE-5]]:1}:"unsafe "
}
