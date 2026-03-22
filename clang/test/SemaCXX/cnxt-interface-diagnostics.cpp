// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

interface CounterLike {
  int next(); // expected-note {{interface method 'next' is declared here}}
};

interface ResetLike {
  void reset(); // expected-note {{interface method 'reset' is declared here}}
};

struct NotInterface {}; // expected-note {{'NotInterface' declared here}}

class MissingReset implements CounterLike, ResetLike { // expected-error {{cNxt class 'MissingReset' is missing interface method 'reset' required by 'ResetLike'}}
public:
  int next();
};

class WrongNext implements CounterLike {
public:
  int next(int); // expected-error {{cNxt class 'WrongNext' has method 'next' with incompatible signature for interface 'CounterLike'}}
};

interface ReadsNumber {
  int next(); // expected-note {{interface method 'next' from 'ReadsNumber' is declared here}}
};

interface ResetsCounter {
  void next(); // expected-note {{interface method 'next' from 'ResetsCounter' is declared here}}
};

class ConflictingInterfaces implements ReadsNumber, ResetsCounter { // expected-error {{cNxt class 'ConflictingInterfaces' has conflicting interface requirements for method 'next' from 'ReadsNumber' and 'ResetsCounter'}}
};

class InvalidImplements implements NotInterface, CounterLike { // expected-error {{cNxt class 'InvalidImplements' can only implement interface types; 'NotInterface' is not an interface}}
public:
  int next();
};
