// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

void sema_runtime_surface(unique<int> strong, shared<int> owner,
                          weak<int> observer) {
  unique<int> copied = strong; // expected-error {{call to deleted constructor of 'unique<int>'}}
  // expected-note@* {{'unique' has been explicitly marked deleted here}}
  shared<int> widened = share(static_cast<unique<int> &&>(strong));
  shared<int> copied_owner = owner;
  weak<int> aliased(owner);
  shared<int> recovered = observer.lock();
  shared<int> bad_shared;
  unique<int> bad_unique;
  bad_shared = observer; // expected-error {{cNxt cannot convert ownership handle 'weak' to 'shared'; valid flow is unique -> shared -> weak}}
  bad_unique = owner;    // expected-error {{cNxt cannot convert ownership handle 'shared' to 'unique'; valid flow is unique -> shared -> weak}}
  (void)observer.get();  // expected-error {{no member named 'get'}}
  (void)widened.get();
  (void)copied_owner.get();
  (void)aliased.expired();
  (void)recovered.get();
}
