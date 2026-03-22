// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s
// expected-no-diagnostics

interface CounterLike {
  int next();
};

__cnxt_iface_borrowed<CounterLike> default_view;

__cnxt_iface_borrowed<CounterLike>
forward(__cnxt_iface_borrowed<CounterLike> view) {
  return view;
}

void use() {
  __cnxt_iface_borrowed<CounterLike> local = forward(default_view);
  (void)local.__object();
  (void)local.__witness();
}
