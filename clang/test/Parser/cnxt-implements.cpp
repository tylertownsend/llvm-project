// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

interface CounterLike {
  int next();
};

interface Resettable {
  void reset();
};

class Counter implements CounterLike, Resettable {
  int value;
  int next();
  void reset();
};

class PlainCounter {
  int value;
};

class BadCounter
    : CounterLike { // expected-error {{cNxt does not support inheritance base clauses}}
};

int implements = 0;

void use_identifier() {
  implements = 1;
}
