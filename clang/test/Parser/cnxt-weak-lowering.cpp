// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s
// expected-no-diagnostics

void touch_weak(weak<int> observer) {
  (void)observer.expired();
  shared<int> owner = observer.lock();
  (void)owner.use_count();
}
