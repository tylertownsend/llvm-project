// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s
// expected-no-diagnostics

interface CounterLike {
  int next();
};

class Counter implements CounterLike {
public:
  int next();
};

CounterLike global_view;

void takes(CounterLike view);

CounterLike returns(Counter &counter) {
  CounterLike local = counter;
  return local;
}

void use(Counter &counter) {
  CounterLike local = counter;
  takes(counter);
  CounterLike other = returns(counter);
  (void)local;
  (void)other;
}
