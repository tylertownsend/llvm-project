// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

interface CounterLike {
  int next(); // expected-note 2{{interface method 'next' is declared here}}
  void reset(); // expected-note {{interface method 'reset' is declared here}}
};

class Good implements CounterLike {
public:
  int next();
  void reset();
};

class MissingReset implements CounterLike { // expected-error {{cNxt class 'MissingReset' is missing interface method 'reset' required by 'CounterLike'}}
public:
  int next();
};

class WrongNext implements CounterLike {
public:
  int next(int); // expected-error {{cNxt class 'WrongNext' has method 'next' with incompatible signature for interface 'CounterLike'}}
  void reset();
};

class PrivateNext implements CounterLike {
  int next(); // expected-error {{cNxt class 'PrivateNext' must make method 'next' public to satisfy interface 'CounterLike'}}
public:
  void reset();
};
