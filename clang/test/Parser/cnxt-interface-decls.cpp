// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

interface CounterLike;

interface CounterLike {
  int next();
  void reset();
};

CounterLike &pass_through(CounterLike &value) {
  return value;
}

int interface = 0;

void update_name() {
  interface = 1;
}

interface Derived
    : CounterLike { // expected-error {{cNxt does not support inheritance base clauses}}
};
