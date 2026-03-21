// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

struct Pair {
  int first;
  int second;
};

void accepts_make_construction() {
  unique<int> zero = make<int>();
  unique<int> one = make<int>(42);
  unique<Pair> pair = make<Pair>(1, 2);
  (void)zero;
  (void)one;
  (void)pair;
}

void reject_non_construction_template_ids() {
  vector<int> value; // expected-error {{cNxt does not support template argument lists}}
}
