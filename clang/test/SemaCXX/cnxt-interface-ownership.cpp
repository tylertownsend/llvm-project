// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s
// expected-no-diagnostics

interface CounterLike {
  int next();
};

class Counter implements CounterLike {
public:
  int next();
};

unique<CounterLike> make_iface_owner() {
  return make<Counter>();
}

shared<CounterLike> make_iface_shared() {
  unique<Counter> concrete = make<Counter>();
  return share(static_cast<unique<Counter> &&>(concrete));
}

shared<CounterLike> share_iface_owner(unique<CounterLike> owner) {
  return share(static_cast<unique<CounterLike> &&>(owner));
}

weak<CounterLike> observe(shared<CounterLike> owner) {
  return owner;
}

int from_unique(unique<CounterLike> owner) {
  return owner.next();
}

int from_shared(shared<CounterLike> owner) {
  return owner.next();
}

int from_locked(weak<CounterLike> observer) {
  return observer.lock().next();
}
