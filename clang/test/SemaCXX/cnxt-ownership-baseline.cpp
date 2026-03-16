// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

void ownership_baseline(unique<int> unique_lhs, unique<int> unique_rhs,
                        shared<int> shared_lhs, shared<int> shared_rhs,
                        weak<int> weak_rhs) {
  shared_lhs = shared_rhs;
  shared_lhs = weak_rhs.lock();
  if (weak_rhs.expired()) {
    shared_rhs = shared_lhs;
  }

  unique_lhs = shared_lhs; // expected-error {{cNxt cannot convert ownership handle 'shared' to 'unique'; valid flow is unique -> shared -> weak}}
  shared_lhs = weak_rhs;   // expected-error {{cNxt cannot convert ownership handle 'weak' to 'shared'; valid flow is unique -> shared -> weak}}
}
