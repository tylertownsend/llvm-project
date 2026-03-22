// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

interface CounterLike;
interface Resettable;

interface CounterLike {
  int next();
  void reset();
};

interface Resettable {
  void reset();
};

class Counter implements CounterLike, Resettable {
public:
  int state;
  int next();
  void reset();
};

CounterLike &pass_through(CounterLike &value) {
  return value;
}

CounterLike make_view(Counter value);
Resettable make_resetter(Counter &value);

int interface = 0;

void update_name() {
  interface = 1;
}

interface Derived
    : CounterLike { // expected-error {{cNxt does not support inheritance base clauses}}
};
