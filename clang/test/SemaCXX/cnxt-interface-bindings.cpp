// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s
// expected-no-diagnostics

interface CounterLike {
  int next();
};

interface Resettable {
  void reset();
};

class Counter implements CounterLike, Resettable {
public:
  int next();
  void reset();
};

CounterLike global_view;
Resettable global_resetter;

void takes(CounterLike view);
void takes_reset(Resettable view);

CounterLike returns(Counter &counter) {
  CounterLike local = counter;
  return local;
}

Resettable returns_reset(Counter &counter) {
  Resettable local = counter;
  return local;
}

void use(Counter &counter) {
  CounterLike local = counter;
  Resettable resetter = counter;
  takes(counter);
  takes_reset(counter);
  CounterLike other = returns(counter);
  Resettable other_resetter = returns_reset(counter);
  (void)local;
  (void)resetter;
  (void)other;
  (void)other_resetter;
}
