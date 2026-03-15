// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s
// expected-no-diagnostics

void copy_and_assign_shared(shared<int> first, shared<int> second) {
  shared<int> copied = first;
  copied = second;
  (void)copied.use_count();
}
