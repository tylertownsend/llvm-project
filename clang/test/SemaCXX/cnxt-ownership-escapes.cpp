// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify -verify-ignore-unexpected=note %s

void reject_safe_handle_escapes(unique<int> unique_owner,
                                shared<int> shared_owner) {
  (void)unique_owner.get();     // expected-error {{cNxt does not allow ownership handle raw-pointer escape via 'get' outside unsafe FFI boundaries}}
  (void)unique_owner.release(); // expected-error {{cNxt does not allow ownership handle raw-pointer escape via 'release' outside unsafe FFI boundaries}}
  (void)shared_owner.get();     // expected-error {{cNxt does not allow ownership handle raw-pointer escape via 'get' outside unsafe FFI boundaries}}
}

extern "C" void reject_plain_extern_handle_escapes(
    unique<int> unique_owner, shared<int> shared_owner) {
  (void)unique_owner.get();     // expected-error {{cNxt does not allow ownership handle raw-pointer escape via 'get' outside unsafe FFI boundaries}}
  (void)unique_owner.release(); // expected-error {{cNxt does not allow ownership handle raw-pointer escape via 'release' outside unsafe FFI boundaries}}
  (void)shared_owner.get();     // expected-error {{cNxt does not allow ownership handle raw-pointer escape via 'get' outside unsafe FFI boundaries}}
}

unsafe extern "C" void allow_ffi_handle_escapes(unique<int> unique_owner,
                                                 shared<int> shared_owner) {
  (void)unique_owner.get();
  (void)unique_owner.release();
  (void)shared_owner.get();
}
