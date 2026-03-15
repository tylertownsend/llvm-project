// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

void reject_illegal_ownership_conversions(unique<int> unique_handle,
                                          shared<int> shared_handle,
                                          weak<int> weak_handle) {
  unique_handle = shared_handle; // expected-error {{cNxt cannot convert ownership handle 'shared' to 'unique'; valid flow is unique -> shared -> weak}}
  shared_handle = weak_handle;   // expected-error {{cNxt cannot convert ownership handle 'weak' to 'shared'; valid flow is unique -> shared -> weak}}
  unique_handle = weak_handle;   // expected-error {{cNxt cannot convert ownership handle 'weak' to 'unique'; valid flow is unique -> shared -> weak}}
}
