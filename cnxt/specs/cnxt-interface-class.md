# cNxt Interface/Class Model

Status: Milestone 8 interface/class baseline.

This document defines the intended cNxt-native surface for interface-oriented
programming and concrete class conformance without exposing C++ inheritance
syntax or requiring user-written ABI glue.

## Goals

- provide one explicit way to declare behavior contracts (`interface`)
- let concrete cNxt types opt into those contracts with a native
  `implements` surface
- support dynamic dispatch in ordinary cNxt code without manual vtable
  structs or `extern "C"` adapters
- keep ownership and dispatch composable so later milestones can support
  `unique<Interface>` and `shared<Interface>` cleanly

## Non-Goals (M8 baseline)

- C++ base clauses or implicit inheritance syntax
- stored fields inside interfaces
- interface inheritance
- default method bodies in interfaces
- multiple concrete base classes
- exposing raw function-pointer tables in user source
- defining ownership-handle behavior for interface values; that is deferred to
  M8-07

## Terms

- `interface`: a named method contract with no stored state
- `class`: a concrete nominal type that may store fields, define methods, and
  explicitly implement one or more interfaces
- `conformance`: the compile-time proof that a class satisfies an interface's
  required method set
- `witness table`: compiler-generated dispatch table that maps an interface's
  required methods to the concrete class implementations

## User-Facing Surface

### Interface declarations

An interface declaration names a method contract:

```cnxt
interface CounterLike {
  fn next() -> int
  fn reset() -> void
}
```

Rules:

- interface bodies may contain method signatures only
- interface methods have no bodies in the M8 baseline
- interface methods do not declare stored fields
- interfaces are nominal: two interfaces with identical method sets are still
  distinct types

### Class declarations

A class declaration introduces a concrete nominal type:

```cnxt
class Counter {
  value: int

  fn init(value: int)
  fn next() -> int
  fn reset() -> void
}
```

M8 adds an explicit conformance clause:

```cnxt
class Counter implements CounterLike {
  value: int

  fn init(value: int)
  fn next() -> int { return value + 1 }
  fn reset() -> void { value = 0 }
}
```

Rules:

- `implements` is the only class-to-interface binding syntax
- C++-style `class Counter : CounterLike` is not part of the cNxt surface
- a class may list zero or more interfaces in a comma-separated
  `implements` clause
- class member-body syntax follows the ordinary cNxt field and method
  declaration grammar; this document only fixes the interface/conformance
  surface

## Conformance Rules

A class conforms to an interface only when it explicitly names that interface
in its `implements` clause and provides a compatible implementation for every
required method.

Method matching rules:

- method name must match exactly
- parameter count must match exactly
- parameter types must match exactly after name lookup and alias resolution
- result type must match exactly
- receiver mutability and any later effect markers must be at least as strict
  as the interface contract requires

Additional rules:

- extra class methods are allowed
- interface methods are part of the class's public callable surface
- a class may implement multiple interfaces when their required method sets are
  jointly satisfiable
- if two interfaces require the same method name with incompatible signatures,
  the class is ill-formed
- a class that omits any required interface method is ill-formed

## Dispatch Semantics

Concrete calls stay direct:

```cnxt
let counter = Counter(1)
counter.next()
```

Calls through an interface-typed binding are dynamically dispatched:

```cnxt
let view: CounterLike = counter
view.next()
```

Baseline dispatch model:

- an interface value is represented as:
  1. a reference to the concrete object
  2. a compiler-generated witness table for the chosen interface
- each witness table stores one entry per required interface method
- dynamic calls load the method entry from the witness table and pass the
  concrete object reference as the receiver
- direct calls on a known concrete class do not use the witness table

ABI expectations:

- witness-table layout is compiler-owned and stable for cNxt-only programs
- user code does not spell witness tables, vtables, or raw function pointers
- user code does not need `extern "C"` shims to call interface methods

## Ownership Interaction

M8-01 defines only the interface/class model itself. Ownership integration for
interface values is intentionally deferred.

Baseline rule:

- ordinary interface-typed bindings behave as borrowed views over a concrete
  object

Deferred to M8-07:

- `unique<Interface>`
- `shared<Interface>`
- `weak<Interface>`
- object-lifetime rules for owned interface values

## Diagnostics Expectations

The frontend should produce cNxt-specific diagnostics for:

- unknown names in `implements` clauses
- attempting to implement a non-interface type
- missing required methods
- method signature mismatches
- duplicate or ambiguous interface bindings
- forbidden interface features in the baseline:
  - stored fields
  - default bodies
  - interface inheritance
  - C++ base-clause syntax in cNxt mode

## Transition Notes

- existing transitional examples may still use plain structs and C++-style
  methods where later milestones have not yet introduced the full cNxt-native
  `class` parser surface
- Milestone 8 implementation work should converge user-facing examples on the
  `interface` / `class` / `implements` spelling defined here

## Acceptance Criteria for M8-01

- this spec is the source of truth for the `interface` and `class` baseline
  surface
- follow-on parser work can implement `interface` declarations and
  `implements` clauses directly from this document
- follow-on sema/codegen work can derive conformance diagnostics and
  witness-table dispatch behavior from this document
