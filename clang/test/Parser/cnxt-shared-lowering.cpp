// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s
// expected-no-diagnostics

void touch_shared(shared<int> owner) {
  (void)owner.use_count();
  owner.reset();
}
