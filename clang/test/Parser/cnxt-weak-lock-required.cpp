// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

void reject_direct_weak_access(weak<int> observer) {
  (void)observer.get(); // expected-error {{no member named 'get'}}
}

void require_lock_before_use(weak<int> observer) {
  shared<int> owner = observer.lock();
  (void)owner.use_count();
}
