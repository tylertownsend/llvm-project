// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

void range_for_ok() {
  int values[2] = {1, 2};
  for (int value : values) {
    (void)value;
  }

  while (false) {
  }
}

void reject_goto() {
  goto done; // expected-error {{cNxt does not support goto statements}}
done:
  return;
}

void reject_do() {
  do { // expected-error {{cNxt does not support do/while statements}}
  } while (false);
}

void reject_c_style_for() {
  for (;;) { // expected-error {{cNxt only supports range-based 'for' loops}}
  }
}

void reject_try() {
  try { // expected-error {{cNxt does not support try/catch statements}}
  } catch (...) {
  }
}

void reject_throw() {
  throw 1; // expected-error {{cNxt does not support throw expressions}}
}

void reject_new() {
  new int(1); // expected-error {{cNxt does not support 'new' expressions}}
}

unsafe extern "C" void reject_delete(int *ptr) {
  delete ptr; // expected-error {{cNxt does not support 'delete' expressions}}
}

struct Base {};

struct Derived
    : Base { // expected-error {{cNxt does not support inheritance base clauses}}
};

struct OverloadedOperators {
  int
  operator+(const OverloadedOperators &) const; // expected-error {{cNxt does not support operator overloading declarations}}

  explicit
  operator bool() const; // expected-error {{cNxt does not support operator overloading declarations}}
};

int reject_c_style_cast(double value) {
  return (int)value; // expected-error {{cNxt does not support C-style casts outside unsafe regions}}
}
