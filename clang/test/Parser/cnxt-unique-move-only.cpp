// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

void copy_unique(unique<int> source) {
  unique<int> copied = source; // expected-error {{call to deleted constructor of 'unique<int>'}}
  // expected-note@* {{'unique_ptr' has been explicitly marked deleted here}}
}

void move_unique(unique<int> source) {
  unique<int> moved = static_cast<unique<int> &&>(source);
  (void)moved;
}
