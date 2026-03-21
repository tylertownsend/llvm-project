// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

struct Pair {
  int first;
  int second;
};

void accepts_make_types() {
  unique<int> zero = make<int>();
  unique<int> one = make<int>(42);
  unique<Pair> pair = make<Pair>(1, 2);
  (void)zero;
  (void)one;
  (void)pair;
}

void rejects_non_unique_result() {
  int plain = make<int>(42); // expected-error {{no viable conversion from 'unique<int>' to 'int'}}
  (void)plain;
}
