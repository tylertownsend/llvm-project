// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify -verify-ignore-unexpected=note %s

int *global_ptr; // expected-error {{cNxt does not support raw pointer declarations outside unsafe FFI boundaries}}

struct PointerField {
  int *field; // expected-error {{cNxt does not support raw pointer fields outside unsafe FFI boundaries}}
};

int *non_ffi_signature(int *p); // expected-error {{cNxt does not support raw pointer function signatures outside unsafe FFI boundaries}}
extern "C" int *extern_c_without_unsafe(int *p); // expected-error {{cNxt does not support raw pointer function signatures outside unsafe FFI boundaries}}
cnxt_import_c int *import_c_without_handles(int *p); // expected-error {{cNxt does not support raw pointer function signatures outside unsafe FFI boundaries}}
cnxt_export_c int *export_c_without_handles(int *p); // expected-error {{cNxt does not support raw pointer function signatures outside unsafe FFI boundaries}}

void reject_local_raw_pointer(int value) {
  int *local_ptr; // expected-error {{cNxt does not support raw pointer declarations outside unsafe FFI boundaries}}
  value = value;
}

unsafe extern "C" int *ffi_signature(int *p);
