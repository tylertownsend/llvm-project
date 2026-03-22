// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s
// expected-no-diagnostics

void touch_unique(unique<int> owner) {
  owner.reset();
}
