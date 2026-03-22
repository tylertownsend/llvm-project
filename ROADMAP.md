# ROADMAP

Source plan: `cnxt/docs/commit-plan.md`.

## Priority Queue

- [x] M6-01 Define compiler-owned ownership runtime ABI and symbol contract.
- [x] M6-02 Replace std-header-dependent ownership prelude with compiler-owned handle declarations.
- [x] M6-03 Add runtime library skeleton for `unique/shared/weak` lifetime operations.
- [x] M6-04 Lower ownership operations to runtime calls in CodeGen.
- [x] M6-05 Emit deterministic `unique<T>` drop on all control-flow exits.
- [x] M6-06 Emit reference-count operations for `shared<T>` copy/move/assign.
- [x] M6-07 Emit runtime-backed `weak<T>.lock()` / `.expired()` behavior.
- [x] M6-08 Add diagnostics when ownership runtime linkage is missing or ABI is incompatible.
- [x] M6-09 Remove implicit `<memory>` dependency from cNxt prelude path.
- [x] M6-10 Add parser/sema/codegen regression tests for runtime-backed ownership behavior.
- [x] M6-11 Add runtime leak/double-free smoke tests (ASan/LSan-enabled CI job).
- [x] M6-12 Add an end-to-end cNxt example that allocates and drops a heap object with `unique<T>` and no `extern "C"` declarations.
- [x] M7-01 Specify user-facing construction API (no raw-pointer syntax).
- [x] M7-02 Parse/type-check construction expressions that return `unique<T>`.
- [x] M7-03 Reject invalid `make<T>(...)` payload targets in cNxt safe code.
- [x] M7-04 Lower construction expressions to runtime allocation plus constructor/init calls in CodeGen.
- [x] M7-05 Add builtin conversion API for widening ownership without raw-pointer intermediates.
- [x] M7-06 Restrict ownership-handle raw pointer escape operations in safe code.
- [x] M7-07 Tighten pointer policy from "extern C carveout" to explicit unsafe/FFI boundaries.
- [x] M7-08 Add cNxt diagnostics + fix-its that rewrite pointer-centric usage into ownership-centric forms where safe/possible.
- [x] M7-09 Add control-flow cleanup tests proving deterministic deallocation semantics.
- [x] M7-10 Add end-to-end example: class instance construction, method call, and scope-exit cleanup with no raw-pointer syntax and no glue file.
- [x] M8-01 Write `cnxt/specs/cnxt-interface-class.md` with interface/class syntax, conformance rules, and dispatch semantics.

## Deliverable Status

- [x] M6-01
- [x] M6-02
- [x] M6-03
- [x] M6-08 through M6-10
- [x] M6-11
- [x] M6-12
- [x] M7-01
- [x] M7-02
- [x] M7-03
- [x] M7-04
- [x] M7-05
- [x] M7-06
- [x] M7-07
- [x] M7-08
- [x] M7-09
- [x] M7-10
- [x] M8-01
- [ ] M8-02 through M8-11
- [ ] M9-01 through M9-08
- [ ] M10-01 through M10-06
- [x] M1-01 through M1-12
- [x] M2-01 through M2-14
- [x] M3-00 through M3-13
- [x] M4-01 through M4-14
- [x] M5-01 through M5-09

## Post-M5 Plan (Glue-Free cNxt Compiler)

This section is the proposed path from the current "restricted C++ host mode"
to a user-facing cNxt experience where normal programs do not require
`extern "C"` glue or raw-pointer syntax.

### Milestone 6 - Compiler-Owned Ownership Runtime

Goal: make `unique/shared/weak` semantics runtime-backed and independent of
host C++ `<memory>` headers in user compilation flows.

Deliverables:

- [x] M6-01 Write `cnxt/specs/cnxt-ownership-runtime.md` defining runtime ABI:
  allocation, retain/release, weak-lock/expired, and symbol naming/versioning.
- [x] M6-02 Replace current prelude aliases with compiler-owned ownership handle
  declarations that do not require parsing host `<memory>` in user mode.
- [x] M6-03 Add `cnxt/runtime/ownership/` runtime library skeleton exporting the
  ABI functions required by `unique/shared/weak`.
- [x] M6-04 Lower ownership handle operations in CodeGen to runtime calls
  instead of direct dependence on host STL type internals.
- [x] M6-05 Emit deterministic `unique<T>` destruction on all exits
  (fallthrough, `return`, `break`, `continue`) for local ownership bindings.
- [x] M6-06 Emit reference-count operations for `shared<T>` copy/move/assign
  sites according to cNxt assignment rules.
- [x] M6-07 Emit runtime-backed `weak<T>.lock()` / `.expired()` behavior with
  explicit nullability semantics.
- [x] M6-08 Add diagnostics when ownership runtime linkage is missing or ABI is
  incompatible (`-x cnxt` should fail fast with cNxt-specific messaging).
- [x] M6-09 Remove implicit `<memory>` inclusion/`__has_include(<memory>)`
  dependence from cNxt prelude path.
- [x] M6-10 Add parser/sema/codegen regression tests for runtime-backed
  ownership behavior in `clang/test/{Parser,SemaCXX,CodeGenCXX}`.
- [x] M6-11 Add runtime leak/double-free smoke tests (ASan/LSan-enabled CI job).
- [x] M6-12 Add an end-to-end cNxt example that allocates and drops a heap
  object with `unique<T>` and no `extern "C"` declarations.

### Milestone 7 - Construction Surface Without Raw Pointers

Goal: allow user code to allocate owned objects directly in cNxt syntax, with
automatic lifetime semantics and no raw-pointer escape hatches in safe code.

Deliverables:

- [x] M7-01 Define construction syntax/API in spec (for example `make<T>(...)`)
  and its ownership/lifetime contract.
- [x] M7-02 Implement parser support for cNxt construction expressions.
- [x] M7-03 Implement Sema rules so construction expressions type-check to
  `unique<T>` and reject pointer-returning construction in safe code.
- [x] M7-04 Lower construction expressions to runtime allocation plus
  constructor/init calls in CodeGen.
- [x] M7-05 Add builtin conversion API for widening ownership
  (`share(unique<T>) -> shared<T>`) without raw pointer intermediates.
- [x] M7-06 Restrict ownership-handle raw pointer escape operations (such as
  unrestricted `.get()`) to explicit unsafe/FFI contexts.
- [x] M7-07 Tighten pointer policy from "extern C carveout" to explicit
  `unsafe extern` boundary model for pointer-bearing signatures.
- [x] M7-08 Add cNxt diagnostics + fix-its that rewrite pointer-centric usage
  into ownership-centric forms where safe/possible.
- [x] M7-09 Add control-flow cleanup tests (early return/branch paths) proving
  deterministic deallocation semantics.
- [x] M7-10 Add end-to-end example: class instance construction, method call,
  and scope-exit cleanup with no raw-pointer syntax and no glue file.

### Milestone 8 - Interface/Class Model (No C++ Inheritance Syntax)

Goal: support interface-style programming and implementation binding in cNxt
without requiring C++ base clauses or manual ABI glue.

Deliverables:

- [x] M8-01 Write `cnxt/specs/cnxt-interface-class.md` with interface/class
  syntax, conformance rules, and dispatch semantics.
- [ ] M8-02 Add parser support for `interface` declarations in cNxt mode.
- [ ] M8-03 Add parser support for class-to-interface implementation syntax
  (cNxt-native spelling, not C++ `: Base` inheritance syntax).
- [ ] M8-04 Add Sema conformance checks: required methods, signature matching,
  visibility, and implementation completeness diagnostics.
- [ ] M8-05 Implement dispatch representation (vtable/witness-table style) with
  stable ABI for cNxt-only programs.
- [ ] M8-06 Implement CodeGen lowering for dynamic interface dispatch calls.
- [ ] M8-07 Integrate ownership handles with interface values
  (`unique<Interface>`, `shared<Interface>` behavior rules).
- [ ] M8-08 Add focused diagnostics for missing implementations, invalid
  overrides, and ambiguous interface bindings.
- [ ] M8-09 Update clangd/IDE support for interface/class syntax and symbols.
- [ ] M8-10 Add parser/sema/codegen regression coverage for interface/class
  declarations, conformance, and dispatch.
- [ ] M8-11 Add end-to-end cNxt interface+class sample with unique ownership
  and zero `extern "C"` declarations.

### Milestone 9 - FFI Containment and No-Glue Standard Library Surface

Goal: keep interop available but contained, while ordinary app code uses cNxt
stdlib APIs and avoids manual ABI glue.

Deliverables:

- [ ] M9-01 Specify `unsafe extern` boundary model in
  `cnxt/specs/cnxt-ffi-boundary.md` (where pointers are legal and why).
- [ ] M9-02 Add safe stdlib modules for basic app entrypoints (for example
  output/logging) so hello-world style programs need no manual extern imports.
- [ ] M9-03 Add compiler-generated ABI thunk support for exporting/importing
  cNxt functions through C ABI without user-written glue wrappers.
- [ ] M9-04 Add ownership-handle marshalling rules across ABI thunks.
- [ ] M9-05 Enforce raw-pointer ban in safe modules with lint + compiler
  diagnostics aligned to `unsafe extern` policy.
- [ ] M9-06 Add mixed-language interoperability tests validating generated thunk
  paths for cNxt <-> C/C++ calls.
- [ ] M9-07 Add migration guide from legacy manual `extern "C"` patterns to
  compiler-managed interop boundaries.
- [ ] M9-08 Update `cnxt new`/starter template so generated apps compile/run
  without glue files or raw-pointer syntax.

### Milestone 10 - Hardening and Release Gate

Goal: make the no-glue ownership/interface path stable enough for default use.

Deliverables:

- [ ] M10-01 Add stress tests for ownership runtime correctness (leak, UAF,
  double-free, weak-lock races where applicable).
- [ ] M10-02 Add parser/sema fuzz inputs around ownership, construction,
  interface, and `unsafe extern` boundaries.
- [ ] M10-03 Add performance baselines for ownership operations and dispatch
  overhead versus current branch behavior.
- [ ] M10-04 Add CI matrix coverage (Linux/macOS) building and testing runtime +
  compiler features introduced in M6-M9.
- [ ] M10-05 Publish quickstart docs proving normal app development requires no
  manual `extern "C"` glue.
- [ ] M10-06 Add final acceptance checklist and gate milestone completion on an
  end-to-end no-glue sample app test in CI.

## Completion Log

### 2026-03-21 - M8-01

- Completed item: write the Milestone 8 source-of-truth spec for cNxt
  interfaces, classes, explicit conformance, and dynamic dispatch.
- What changed:
  - added `cnxt/specs/cnxt-interface-class.md` defining the baseline
    `interface` surface, `class ... implements ...` spelling, method-matching
    conformance rules, and compiler-owned witness-table dispatch semantics.
  - explicitly scoped out interface inheritance, default interface methods,
    raw vtable exposure, and ownership-handle integration for interface values
    so follow-on milestones have a stable, narrow contract to implement.
  - documented the transition expectation that existing struct-based examples
    are temporary and should converge on the new `interface` / `class` /
    `implements` spellings as Milestone 8 lands.
- Follow-up notes:
  - the spec now fixes the intended language surface, but there is no parser
    support yet; M8-02 should add `interface` parsing directly from this
    document.
- What is now unblocked:
  - M8-02 can implement `interface` declarations against a stable syntax spec.
  - M8-03 can add `implements` parsing without reopening surface design.
  - later M8 sema/codegen work can target a fixed witness-table model.
- Direction check:
  - roadmap remains directionally correct; M8-02 is next because parser support
    is the first implementation step on the now-specified interface surface.

### 2026-03-21 - M7-10

- Completed item: add the Milestone 7 end-to-end no-glue sample showing class
  construction, method use, and scope-exit cleanup through the compiler-owned
  ownership surface.
- What changed:
  - added `cnxt/examples/ownership/class-method.cn`, a runtime-backed example
    that constructs a stack `Counter`, calls `seed.next()`, then constructs an
    owned `unique<Counter>` via `make<Counter>(...)` and relies on scope-exit
    cleanup for the heap-owned instance.
  - updated `cnxt/README.md` so the documented build/run commands now use the
    new class-method example and explicitly call out that the sample requires
    no raw-pointer allocation syntax, no user-written `extern "C"` declarations,
    and no glue file.
  - repointed the existing driver smoke test to the new example so the branch
    keeps an executable end-to-end proof of the no-glue ownership flow.
- Follow-up notes:
  - Milestone 7 is now complete; the next major gap is Milestone 8's
    interface/class model, which still needs a cNxt-native implementation
    syntax beyond plain C++-style structs and methods.
- What is now unblocked:
  - Milestone 8 work can build on a stable ownership example that already
    exercises construction, method use, runtime linking, and automatic cleanup
    without adapter code.
- Direction check:
  - roadmap remains directionally correct; Milestone 7 is complete and the next
    highest-priority unblocked deliverable is `M8-01`.

### 2026-03-21 - M7-09

- Completed item: add targeted control-flow cleanup tests proving
  deterministic deallocation for constructed and widened ownership values.
- What changed:
  - added `clang/test/CodeGenCXX/cnxt-ownership-cleanup-paths.cpp` with a
    `make<T>(...)` early-return case that proves both branches flow through a
    shared cleanup block which destroys the local `unique<T>`.
  - added a branch-local `share(make<T>(...))` case that proves the temporary
    `unique<T>` cleanup and the widened `shared<T>` release both execute before
    control rejoins the outer block.
  - kept the checks FileCheck-visible at the IR control-flow level so the test
    locks in cleanup-block shape instead of only looking for destructor calls
    somewhere in the function.
- Follow-up notes:
  - Milestone 7 now has the required cleanup-path proof for the compiler-owned
    construction and widening surfaces; the remaining gap is the end-to-end
    no-glue sample in M7-10.
- What is now unblocked:
  - M7-10 can present the final sample knowing the underlying ownership
    surfaces have explicit cleanup-path coverage for both construction and
    post-construction widening.
- Direction check:
  - roadmap remains directionally correct; M7-10 is next because Milestone 7's
    remaining work is integration/demo polish rather than core semantics.

### 2026-03-21 - M7-08

- Completed item: add cNxt-specific ownership guidance notes plus targeted
  fix-its for pointer-centric declarations and explicit FFI boundary upgrades.
- What changed:
  - added `note_cnxt_prefer_ownership_surfaces`,
    `note_cnxt_prefer_handle_flow`, and `note_cnxt_use_unsafe_extern` so cNxt
    raw-pointer declaration/signature/escape diagnostics now point users toward
    `unique<T>`, `make<T>(...)`, direct handle flow, and `share(...)`.
  - taught raw-pointer function-signature diagnostics to attach an `unsafe `
    fix-it before plain `extern "C"` boundaries, while raw-pointer variable and
    field rejections now emit ownership-surface guidance instead of a bare
    policy error.
  - recorded the actual `extern` source location on cNxt extern declarations
    so later ownership-handle escape diagnostics can reuse the same precise
    `unsafe extern "C"` fix-it inside function bodies.
  - added `clang/test/SemaCXX/cnxt-pointer-guidance-fixits.cpp` to pin the new
    parseable-fixit output and relaxed the existing `-verify` ownership/pointer
    tests to ignore the newly intentional note diagnostics.
- Follow-up notes:
  - the diagnostics are now actionable, but cleanup behavior still needs more
    path-sensitive proof beyond the existing happy-path drops; M7-09 should add
    focused early-return and branch coverage around construction/widening flows.
- What is now unblocked:
  - M7-09 can extend cleanup-path coverage without first stabilizing the user
    guidance surface for rejected pointer-centric code.
  - M7-10 can lean on compiler-provided diagnostics when presenting the
    no-glue ownership example.
- Direction check:
  - roadmap remains directionally correct; M7-09 is next because the remaining
    gap in Milestone 7 is proof of deterministic cleanup behavior, not surface
    syntax or diagnostics.

### 2026-03-21 - M7-07

- Completed item: replace the implicit `extern "C"` raw-pointer carveout with
  an explicit `unsafe extern "C"` boundary model for pointer-bearing cNxt
  signatures and ownership-handle raw escapes.
- What changed:
  - added a contextual cNxt `unsafe` declaration marker before `extern` in the
    parser and threaded that marker through `DeclSpec`.
  - recorded `unsafe extern` functions on the resulting `FunctionDecl` and
    switched raw-pointer signature validation from `isExternC()` to the new
    explicit unsafe-extern annotation.
  - switched ownership-handle raw escape checks (`.get()` / `.release()`) from
    the old plain-`extern "C"` allowance to the same explicit unsafe-extern
    gate.
  - updated parser, `SemaCXX`, and codegen coverage so plain `extern "C"` now
    remains rejected for raw-pointer signatures/escapes while
    `unsafe extern "C"` is accepted where the tests intentionally exercise FFI
    lowering.
- Follow-up notes:
  - the boundary marker now exists and is enforced, but diagnostics still tell
    users only that pointer-centric code is unsupported; M7-08 should add
    targeted cNxt fix-its and guidance toward `make<T>(...)`, `share(...)`,
    and safe ownership surfaces.
- What is now unblocked:
  - M7-08 can offer fix-its against a stable explicit boundary model instead of
    heuristics based on linkage alone.
  - M7-09 can add cleanup-path coverage for mixed safe/unsafe boundary flows
    without the old extern-C ambiguity.
  - M7-10 can present the no-glue example knowing that raw-pointer escape
    syntax is no longer silently available in ordinary foreign-linkage code.
- Direction check:
  - roadmap remains directionally correct; M7-08 is next because the remaining
    gap is developer ergonomics, not core policy enforcement.

### 2026-03-21 - M7-06

- Completed item: restrict ownership-handle raw-pointer escape operations in
  safe cNxt code so `.get()` / `.release()` only remain available at explicit
  FFI boundaries.
- What changed:
  - added a cNxt-specific `err_cnxt_ownership_raw_escape` diagnostic and wired
    ownership escape checking into `BuildCallExpr` early enough to catch bound
    member calls such as `unique<T>::get()` and `shared<T>::get()`.
  - limited the current carveout to system-header code and `extern "C"`
    function bodies, which preserves compiler-owned prelude lowering and
    transitional FFI entry points while rejecting safe-code escape hatches.
  - updated parser and `SemaCXX` surface tests to stop using `.get()` in safe
    code, and added `clang/test/SemaCXX/cnxt-ownership-escapes.cpp` to pin the
    accepted/rejected boundary behavior.
  - updated `cnxt/examples/ownership/unique-heap.cn` so the end-to-end example
    stays fully within safe ownership semantics after the new restriction.
- Follow-up notes:
  - this still models the boundary as a broad `extern "C"` carveout; M7-07
    should replace that with an explicit cNxt `unsafe extern` policy so raw
    pointers are not implicitly allowed throughout all foreign-linkage bodies.
- What is now unblocked:
  - M7-07 can narrow pointer-bearing signatures and raw-pointer escape points
    to an explicit unsafe boundary model instead of today's linkage-based
    approximation.
  - M7-08 can build diagnostics and fix-its on top of a stable raw-escape
    rejection surface.
  - M7-10 can present a no-glue sample that no longer depends on `.get()` even
    for trivial success-path checks.
- Direction check:
  - roadmap remains directionally correct; M7-07 is next because the largest
    remaining gap is that raw-pointer permission is still inferred from
    `extern "C"` instead of an explicit unsafe FFI construct.

### 2026-03-21 - M7-05

- Completed item: add a compiler-owned widening API so cNxt code can convert
  `unique<T>` into `shared<T>` without spelling raw pointers or runtime ABI
  calls in user source.
- What changed:
  - extended the injected cNxt prelude with the runtime declaration for
    `__cnxt_rt_own_v1_shared_from_unique` and a new `share(unique<T> &&)`
    helper that lowers unique-to-shared widening through that ABI.
  - added compiler-owned payload metadata helpers so unique cleanup and shared
    widening can preserve destructor/size/alignment information without
    injecting host STL ownership types.
  - updated the construction spec to name `share(unique<T>) -> shared<T>` as
    the explicit widening step after `make<T>(...)`.
  - added parser, `SemaCXX`, preprocessor, and codegen coverage for the new
    widening surface, including a non-trivial payload case that proves the
    runtime receives destructor metadata.
- Follow-up notes:
  - widening now has a glue-free compiler-owned path, but raw-pointer escape
    methods like `unique<T>::get()` / `release()` still exist on the handle
    surface and need policy tightening in M7-06.
- What is now unblocked:
  - M7-06 can narrow the remaining handle escape hatches without blocking
    shared ownership adoption for safe-code construction flows.
  - M7-09 can cover cleanup behavior for values that are widened from unique to
    shared ownership mid-scope.
  - M7-10 can show object construction plus shared ownership adoption without
    any raw-pointer glue in the sample path.
- Direction check:
  - roadmap remains directionally correct; M7-06 is next because the language
    now has the intended construction and widening surfaces, and the highest
    remaining safety risk is unrestricted raw-pointer escape on ownership
    handles.

### 2026-03-21 - M7-04

- Completed item: lower valid cNxt `make<T>(...)` construction calls to the
  ownership runtime allocation path plus in-place initialization, with no
  user-authored glue required.
- What changed:
  - replaced the compiler-owned prelude's declaration-only `make<T>(...)`
    surface with a real injected definition that allocates via
    `__cnxt_rt_own_v1_alloc`, constructs the payload in place, and returns the
    resulting `unique<T>`.
  - added a system-header-only placement `new` helper so the injected prelude
    can perform in-place construction while ordinary cNxt user code still gets
    the existing `'new' expressions` rejection.
  - guarded the prelude `make<T>(...)` body with `__is_complete_type(T)` so
    invalid incomplete payloads do not emit extra `sizeof(T)` follow-on errors
    after the intended M7-03 diagnostic.
  - updated the ownership example and README to use the branch's intended
    compiler-owned `make<T>(...)` surface instead of the transitional
    `make_unique(value)` helper.
  - added `clang/test/CodeGenCXX/cnxt-construction.cpp` and adjusted parser
    coverage to pin runtime allocation plus payload initialization lowering.
- Follow-up notes:
  - cNxt now has an executable heap-construction surface for `unique<T>`, but
    widening ownership still requires M7-05 so constructed values can move into
    shared ownership without pointer escape hatches.
- What is now unblocked:
  - M7-05 can build `share(unique<T>)` on top of a real runtime-backed
    construction path instead of a declaration-only placeholder.
  - M7-09 can add cleanup-path coverage for constructed values now that valid
    construction calls emit allocation and initialization IR.
  - M7-10 can use `make<T>(...)` in the end-to-end no-glue sample instead of
    relying on transitional helper naming.
- Direction check:
  - roadmap remains directionally correct; M7-05 is next because ownership
    widening is the highest-value missing operation after construction becomes
    executable.

### 2026-03-21 - M7-03

- Completed item: enforce cNxt `make<T>(...)` payload restrictions in sema so
  invalid safe-code construction targets fail with cNxt-specific diagnostics.
- What changed:
  - added `err_cnxt_invalid_construction_target` and taught
    `clang/lib/Sema/SemaExpr.cpp` to reject `make<T>(...)` payloads that are
    raw pointers, ownership handles, or incomplete types.
  - added an early explicit-template-argument check for `make<T>(...)` so
    incomplete payloads fail before temporary cleanup instantiation produces
    unrelated errors, while keeping a resolved-call fallback for the same
    diagnostic after overload resolution.
  - tightened the compiler-owned `unique<T>::reset` prelude implementation so
    incomplete payloads do not trigger stray `alignof(T)` diagnostics while the
    intended construction diagnostic is being emitted.
  - extended `clang/test/SemaCXX/cnxt-construction.cpp` to pin the invalid
    payload cases.
- Follow-up notes:
  - `make<T>(...)` now has the intended safe-code semantic guardrails, but it
    is still only a typed surface; M7-04 must lower successful calls to runtime
    allocation plus initialization.
- What is now unblocked:
  - M7-04 can implement lowering against a construction surface that already
    rejects pointer, ownership-handle, and incomplete payload misuse.
  - M7-08 can reuse a stable cNxt-specific construction diagnostic for
    pointer-centric fix-its.
  - M7-09 can focus on cleanup behavior for valid construction paths instead of
    semantic rejection cases.
- Direction check:
  - roadmap remains directionally correct; M7-04 is next because the
    construction parser+sema contract is now established and the remaining gap
    is executable lowering.

### 2026-03-21 - M7-02

- Completed item: admit `make<T>(...)` construction syntax in cNxt parsing and
  pin its basic `unique<T>` type shape.
- What changed:
  - extended the cNxt template-id allowlist in `ParseTemplate.cpp` so
    `make<T>(...)` parses without opening the door to unrelated template-id
    usage.
  - injected a prelude declaration for `template <typename T, typename... Args>
    unique<T> make(Args...);` so syntax-only and sema tests have a concrete
    construction surface to bind against.
  - added `clang/test/Parser/cnxt-construction.cpp` to prove `make<T>()`,
    `make<T>(arg)`, and `make<T>(arg0, arg1)` parse in cNxt mode while
    unrelated template-ids such as `vector<int>` remain rejected.
  - added `clang/test/SemaCXX/cnxt-construction.cpp` to pin that
    `make<T>(...)` type-checks as `unique<T>` rather than an unowned value.
- Follow-up notes:
  - `make<T>(...)` is parser-visible and has a declared type shape, but it is
    not yet a runnable construction path. M7-03 and M7-04 still need to add the
    ownership-specific semantic checks and real lowering/implementation.
  - the temporary Milestone 6 `make_unique(value)` helper remains the only
    working end-to-end construction bridge until the remaining construction
    milestones land.
- What is now unblocked:
  - M7-03 can focus on construction-specific semantic restrictions instead of
    first opening the parser to the intended syntax.
  - M7-04 can lower a fixed parsed surface rather than a speculative syntax.
  - M7-08 diagnostics/fix-its now have an accepted construction spelling to
    target in parser-aware rewrites.
- Direction check:
  - roadmap remains directionally correct; `M7-03` is next because construction
    syntax is now admitted, but the safe-code semantic restrictions are not yet
    enforced.

### 2026-03-21 - M7-01

- Completed item: define the user-facing raw-pointer-free construction API in a
  milestone-specific spec.
- What changed:
  - added `cnxt/specs/cnxt-construction-api.md` defining the intended
    `make<T>(...) -> unique<T>` surface, type rules, safety constraints,
    initialization semantics, ownership semantics, and runtime/lowering
    contract.
  - documented that direct heap construction in safe code should not require
    raw pointers or runtime ABI spellings, and that direct `shared<T>` /
    `weak<T>` construction is out of scope for this baseline.
  - captured the transition plan from the temporary Milestone 6
    `make_unique(value)` helper to the long-term `make<T>(...)` language
    surface.
  - linked the new spec from `cnxt/README.md`.
- Follow-up notes:
  - the spec intentionally defines the long-term API, not the temporary helper
    that exists today for the milestone-6 sample.
  - constructor resolution, diagnostics, and lowering are now implementation
    tasks for M7-02 through M7-04 rather than open API questions.
- What is now unblocked:
  - M7-02 can implement parser support against a fixed spelling and result
    model instead of exploring multiple construction syntaxes in code.
  - M7-03 can derive its type-checking rules directly from the spec’s payload,
    ownership-handle, and raw-pointer restrictions.
  - M7-08 fix-it work now has an explicit target surface for rewriting
    pointer-centric heap allocation into `make<T>(...)`.
- Direction check:
  - roadmap remains directionally correct; `M7-02` is next because the
    construction API contract is now pinned well enough to start parser work.

### 2026-03-21 - M6-12

- Completed item: add an end-to-end cNxt ownership example that allocates heap
  storage, wraps it in `unique<T>`, and runs without user-written
  `extern "C"` declarations.
- What changed:
  - exposed `__cnxt_rt_own_v1_alloc` through the injected cNxt prelude and
    added a compiler-owned `make_unique(value)` helper so a cNxt program can
    allocate an owned heap cell without declaring runtime ABI symbols in user
    code.
  - added `cnxt/examples/ownership/unique-heap.cn` as the milestone-6 sample:
    allocate `unique<int>`, read it back, and rely on automatic scope-exit
    cleanup.
  - updated `cnxt/README.md` with exact commands to build the ownership runtime,
    compile the example with `-x cnxt`, and run it with `LD_LIBRARY_PATH`
    pointing at the runtime library.
  - added `clang/test/Driver/cnxt-ownership-example.c` to build the runtime,
    compile the sample, and execute the resulting binary in a native Linux
    lit test.
- Follow-up notes:
  - `make_unique(value)` is a transitional milestone-6 helper, not the final
    construction surface. Milestone 7 still owns the user-facing construction
    API and broader constructor/lifetime semantics.
- What is now unblocked:
  - M7-01 can write the construction API spec from a working no-`extern "C"`
    example rather than a purely hypothetical surface.
  - M9 quickstarts and starter templates can point at a repo-owned ownership
    sample while the broader no-glue standard library work is still pending.
  - M10 acceptance work now has a concrete end-to-end ownership sample to keep
    alive in CI as the construction surface evolves.
- Direction check:
  - roadmap remains directionally correct; `M7-01` is next because the branch
    now has a runnable no-`extern "C"` ownership sample, but its construction
    API is intentionally temporary and needs formalization.

### 2026-03-21 - M6-11

- Completed item: add ownership-runtime smoke tests for clean lifecycle, leak
  detection, and double-free detection, and run them in a sanitizer-backed CI
  job.
- What changed:
  - extended `cnxt/runtime/ownership/CMakeLists.txt` with `BUILD_TESTING`
    support, a `CNXT_OWNERSHIP_RT_ENABLE_SANITIZERS` option, and runtime/test
    instrumentation flags for AddressSanitizer plus LeakSanitizer.
  - added `cnxt/runtime/ownership/tests/ownership_runtime_smoke.cpp`, a
    standalone ABI-level smoke binary with `clean`, `leak`, and `double_free`
    modes that exercise `unique`, `shared`, and `weak` runtime entry points.
  - added `cnxt/runtime/ownership/cmake/expect_sanitizer_failure.cmake` so the
    leak and double-free tests explicitly require sanitizer failures and match
    the expected ASan/LSan diagnostics rather than relying on generic non-zero
    exits.
  - added `.github/workflows/cnxt-ownership-runtime-sanitizers.yml` to build
    the ownership runtime in isolation and run the smoke suite in CI with
    sanitizer instrumentation enabled.
- What is now unblocked:
  - M6-12 can add an end-to-end ownership example on top of a runtime layer
    that now has direct leak and double-free smoke coverage.
  - M10-01 ownership-runtime hardening can build on an existing sanitizer test
    harness instead of starting from ad hoc process wrappers.
  - M10-04 CI matrix expansion can reuse the dedicated ownership-runtime job as
    the Linux baseline for runtime safety validation.
- Direction check:
  - roadmap remains directionally correct; `M6-12` is the right next item
    because the ownership runtime now has both compiler-side regressions and
    direct sanitizer-backed smoke coverage.

### 2026-03-21 - M6-10

- Completed item: add parser/sema/codegen regression tests for runtime-backed
  ownership behavior.
- What changed:
  - added `clang/test/Parser/cnxt-ownership-runtime-surface.cpp` as a
    syntax-only smoke test for the runtime-backed `unique/shared/weak` surface:
    move-only `unique`, `shared` copy, `weak(shared)` construction,
    `weak.lock()`, `weak.expired()`, and handle methods such as `get()` and
    `reset()`.
  - added `clang/test/SemaCXX/cnxt-ownership-runtime.cpp` to pin sema behavior
    for runtime-backed handles: deleted `unique` copy construction, valid
    `shared`/`weak` flows, invalid ownership assignments, and rejection of
    direct `weak.get()` access.
  - added `clang/test/CodeGenCXX/cnxt-ownership-runtime.cpp` to exercise the
    combined runtime-backed surface in one lowering path and check that the
    emitted IR still routes through the ownership runtime ABI for retain,
    release, lock, expired, and shared payload access.
- What is now unblocked:
  - M6-11 can add leak/double-free smoke tests on top of a broader regression
    net covering parser, sema, and codegen ownership behavior.
  - M6-12 end-to-end examples can rely on a fuller ownership regression suite
    rather than isolated per-method tests only.
  - M7 construction work can expand the ownership surface with better baseline
    protection across all major frontend stages.
- Direction check:
  - roadmap remains directionally correct; M6-11 is the next item because
    runtime safety validation now provides more leverage than adding examples
    before leak/double-free behavior is smoke-tested.

### 2026-03-21 - M6-08

- Completed item: add cNxt-specific diagnostics when ownership runtime linkage
  is missing or ABI is incompatible.
- What changed:
  - added driver option `-fcnxt-ownership-runtime=<path>` so cNxt link jobs can
    point at the ownership runtime explicitly while milestone 6 is still using
    repo-local runtime artifacts.
  - taught the driver to fail fast for `-x cnxt` link jobs when the ownership
    runtime is missing, cannot be loaded, is missing the ABI probe symbol, or
    reports an unsupported ABI version.
  - validated the ABI eagerly with `__cnxt_rt_own_v1_abi_version()` and, on
    success, appended the runtime shared library path to the link inputs so the
    user does not need a separate manual linker argument.
  - added Linux driver coverage in
    `clang/test/Driver/cnxt-ownership-runtime.c` with tiny shared-library
    fixtures for missing-runtime, load-failure, missing-ABI, bad-ABI, and
    successful-link configuration paths.
- What is now unblocked:
  - M6-10 can extend runtime-backed ownership regression coverage knowing the
    driver now has an explicit runtime-link contract.
  - M6-11 leak and double-free smoke testing can run against a driver flow that
    validates runtime ABI before executing tests.
  - M6-12 end-to-end examples can document a concrete runtime configuration
    path instead of relying on unresolved-symbol linker failures.
- Direction check:
  - roadmap remains directionally correct; M6-10 should stay ahead of M7
    because runtime-backed ownership behavior still needs broader parser/sema/
    codegen regression coverage before construction-surface work expands it.

### 2026-03-21 - M6-07

- Completed item: emit runtime-backed `weak<T>.lock()` / `.expired()` behavior with explicit nullability semantics.
- What changed:
  - added `clang/test/CodeGenCXX/cnxt-weak-nullability.cpp` covering default/null `weak<T>` behavior.
  - verified default `weak<T>` construction materializes a null control pointer.
  - verified `weak<T>.lock()` lowers through `__cnxt_rt_own_v1_weak_lock`, and that reading the resulting `shared<T>` goes through `__cnxt_rt_own_v1_shared_get`.
  - verified `weak<T>.expired()` lowers through `__cnxt_rt_own_v1_weak_expired` and converts the runtime byte result to boolean semantics in IR.
- What is now unblocked:
  - M6-10 runtime-backed ownership regression coverage now includes explicit weak nullability semantics.
  - M6-12 end-to-end examples can rely on tested empty-weak behavior when demonstrating ownership state transitions.
  - M8-07 interface ownership integration work can assume baseline weak/shared nullability behavior is covered.
- Direction check:
  - roadmap remains directionally correct; weak-handle behavior is now pinned at the CodeGen/runtime boundary rather than inferred from helper method shape alone.

### 2026-03-21 - M6-09

- Completed item: remove implicit `<memory>` dependency from the cNxt prelude path.
- What changed:
  - strengthened `clang/test/Preprocessor/cnxt-prelude.c` to assert the injected cNxt prelude does not reference `<memory>` or std smart-pointer spellings.
  - added a `-nostdinc++` syntax-only regression in the prelude test so compiler-owned ownership handles remain usable even when host C++ standard library headers are unavailable.
  - verified the current prelude path remains compiler-owned and self-contained for `unique/shared/weak`.
- What is now unblocked:
  - M6-10 ownership regression coverage can rely on an explicit no-`<memory>` invariant.
  - M6-12 end-to-end samples can assume ownership handles are available without host C++ library headers.
  - M7 construction-surface work can build on a header-independent ownership baseline.
- Direction check:
  - roadmap remains directionally correct; the compiler-owned prelude is now guarded against accidental regression back to host `<memory>` coupling.

### 2026-03-21 - M6-06

- Completed item: emit reference-count operations for `shared<T>` copy/move/assign sites.
- What changed:
  - added `clang/test/CodeGenCXX/cnxt-shared-refcount.cpp` covering runtime-backed refcount lowering for:
    - copy construction
    - move construction
    - copy assignment
    - move assignment
    - destruction of local shared handles
  - verified copy construction lowers to `__cnxt_rt_own_v1_shared_retain`.
  - verified destruction and move assignment lower to `__cnxt_rt_own_v1_shared_release`.
  - verified move construction does not emit retain/release traffic and copy assignment emits retain before release.
- What is now unblocked:
  - M6-07 can build on an explicitly tested shared/weak control-block baseline.
  - M6-10 runtime-backed ownership regression coverage now includes both unique and shared handle paths.
  - M6-12 end-to-end ownership examples can rely on tested shared copy/move semantics.
- Direction check:
  - roadmap remains directionally correct; shared-handle refcount semantics are now exercised directly at the CodeGen/runtime boundary instead of being implicit in prelude code alone.

### 2026-03-21 - M6-05

- Completed item: emit deterministic `unique<T>` destruction on all control-flow exits.
- What changed:
  - added a real destructor to injected `unique<T>` in `clang/lib/Frontend/InitPreprocessor.cpp`, routing scope-exit cleanup through `reset()` and therefore `__cnxt_rt_own_v1_unique_drop`.
  - added focused CodeGen coverage in `clang/test/CodeGenCXX/cnxt-unique-cleanup.cpp` proving cleanup runs for local `unique<T>` bindings on:
    - fallthrough
    - `return`
    - `break`
    - `continue`
  - verified the runtime-backed destructor path lowers through `unique` destructor/reset entrypoints before reaching the runtime ABI.
- What is now unblocked:
  - M6-06 can tighten and verify `shared<T>` copy/move/assign retain-release behavior with deterministic `unique<T>` cleanup now in place.
  - M6-10 can expand ownership regression coverage from a working unique-cleanup baseline.
  - M6-12 end-to-end ownership examples can now rely on automatic scope-exit destruction for `unique<T>`.
- Direction check:
  - roadmap remains directionally correct; `unique<T>` now has actual automatic lifetime behavior instead of requiring explicit `reset()`.

### 2026-03-21 - M6-04

- Completed item: lower ownership handle operations to runtime calls in CodeGen.
- What changed:
  - updated cNxt prelude injection in `clang/lib/Frontend/InitPreprocessor.cpp` so ownership handles declare and call ABI v1 runtime symbols (`__cnxt_rt_own_v1_*`) for weak/shared operations and `unique.reset`.
  - switched injected `shared<T>` / `weak<T>` handle internals to runtime control-pointer semantics with retain/release copy/move/destructor behavior routed through runtime calls.
  - expanded cNxt codegen regression checks to assert runtime call lowering for:
    - `weak<T>.lock()` -> `__cnxt_rt_own_v1_weak_lock`
    - `weak<T>.expired()` -> `__cnxt_rt_own_v1_weak_expired`
  - updated tests:
    - `clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp`
    - `clang/test/CodeGenCXX/cnxt-ownership-interop.cpp`
- What is now unblocked:
  - M6-05 can focus on deterministic `unique<T>` drop coverage on all control-flow exits with runtime-backed drop entrypoints already in prelude.
  - M6-06 can tighten `shared<T>` assignment/copy lowering details now that baseline retain/release runtime paths exist.
  - M6-07 can extend runtime-backed weak semantics from baseline lowering to stricter nullability/behavior checks.
- Direction check:
  - roadmap remains directionally correct; ownership lowering now targets compiler-owned runtime ABI symbols instead of prelude-only pointer shims.

### 2026-03-21 - M6-03

- Completed item: add runtime library skeleton for `unique/shared/weak` lifetime operations.
- What changed:
  - added `cnxt/runtime/ownership/` skeleton project with standalone CMake build (`cnxt_ownership_rt` shared library target).
  - added public C ABI header:
    - `cnxt/runtime/ownership/include/cnxt/runtime/ownership.h`
  - added baseline runtime implementation exporting ABI v1 symbols:
    - `cnxt/runtime/ownership/src/ownership_runtime.cpp`
  - added runtime skeleton documentation:
    - `cnxt/runtime/ownership/README.md`
  - linked runtime skeleton path from `cnxt/README.md`.
- What is now unblocked:
  - M6-04 can lower ownership operations in CodeGen to concrete runtime symbols that now exist in source form.
  - M6-08 can add runtime-link diagnostics against an actual runtime library artifact.
  - M6-11 runtime safety/leak checks can evolve from this implementation baseline.
- Direction check:
  - roadmap remains directionally correct; ownership runtime work is now represented by buildable source artifacts rather than spec-only planning.

### 2026-03-21 - M6-02

- Completed item: replace std-header-dependent ownership prelude with compiler-owned handle declarations.
- What changed:
  - updated `clang/lib/Frontend/InitPreprocessor.cpp` to inject compiler-owned `unique<T>`, `shared<T>`, and `weak<T>` template struct declarations directly in `<cnxt-prelude>`.
  - removed implicit `#include <memory>` and std-alias prelude dependency from the cNxt prelude path.
  - updated ownership-kind classification in `clang/lib/Sema/SemaExpr.cpp` to recognize both legacy (`*_ptr`) and compiler-owned (`unique/shared/weak`) handle names during assignment conversion checks.
  - refreshed cNxt prelude/codegen/parser expectations in:
    - `clang/test/Preprocessor/cnxt-prelude.c`
    - `clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp`
    - `clang/test/CodeGenCXX/cnxt-ownership-interop.cpp`
    - `clang/test/Parser/cnxt-unique-move-only.cpp`
- What is now unblocked:
  - M6-03 runtime library skeleton can target compiler-owned handle declarations without std-header coupling.
  - M6-04 CodeGen runtime-call lowering can transition away from std::weak_ptr-specific call expectations.
  - M6-09 prelude cleanup scope is reduced because the core `<memory>` dependency is already removed from injected declarations.
- Direction check:
  - roadmap remains directionally correct; ownership surface is now compiler-owned in user mode, which is required before runtime ABI lowering work.

### 2026-03-21 - M6-01

- Completed item: define compiler-owned ownership runtime ABI and symbol contract.
- What changed:
  - added `cnxt/specs/cnxt-ownership-runtime.md` defining ownership runtime ABI v1 for allocation, unique drop, shared retain/release, and weak lock/expired operations.
  - defined ABI version negotiation and symbol policy using `__cnxt_rt_own_v1_*` naming.
  - documented runtime/CodeGen lowering contract and thread-safety/error model expectations.
  - linked ownership runtime ABI spec from `cnxt/README.md`.
- What is now unblocked:
  - M6-02 can replace std-header-dependent prelude aliases with compiler-owned handle declarations tied to this ABI.
  - M6-03 runtime library skeleton can implement the symbol set defined in this spec without interface ambiguity.
  - M6-04 CodeGen lowering work can target stable symbol names and function signatures.
- Direction check:
  - roadmap remains directionally correct; this establishes a concrete runtime contract needed to remove user-visible ownership glue.

### 2026-03-15 - M2-09

- Completed item: reject template declarations and template argument use in cNxt mode.
- What changed:
  - parser now rejects `template` declarations when `CNxtNoTemplates` is enabled.
  - template-id annotation now emits a direct cNxt error and marks template arguments invalid in cNxt mode.
  - added parser coverage in `clang/test/Parser/cnxt-templates.cpp`.
- What is now unblocked:
  - M2-10 inheritance restrictions can land independently.
  - M2-11 operator overloading restrictions can land independently.
  - M2-14 recovery-oriented restriction test expansion.
- Direction check:
  - roadmap remains directionally correct; this keeps cNxt as an intentionally restricted C++ subset.

### 2026-03-15 - M2-10

- Completed item: reject inheritance and base-specifier syntax in cNxt mode.
- What changed:
  - parser now rejects base clauses (`: Base`) for cNxt class/struct declarations.
  - parser recovery skips base specifiers and resumes at class body parsing.
  - extended `clang/test/Parser/cnxt-restrictions.cpp` with inheritance coverage.
- What is now unblocked:
  - M2-11 operator overloading restrictions can be implemented without base-clause parser conflicts.
  - M2-14 additional restriction recovery tests can include inheritance scenarios.
- Direction check:
  - roadmap remains directionally correct; cNxt restriction enforcement continues to tighten surface area safely.

### 2026-03-15 - M2-11

- Completed item: reject operator overloading declarations in cNxt mode.
- What changed:
  - semantic analysis now rejects operator-function, literal-operator, and conversion-operator declarations in cNxt mode.
  - added cNxt-specific Sema diagnostic: `err_cnxt_unsupported_declaration`.
  - extended `clang/test/Parser/cnxt-restrictions.cpp` with operator-overload rejection coverage.
- What is now unblocked:
  - M2-12 cast restriction work can proceed with clearer operator surface limits.
  - M2-14 can now include operator-overload recovery assertions.
- Direction check:
  - roadmap remains directionally correct; this prevents C++ operator-surface leakage into cNxt.

### 2026-03-15 - M2-12

- Completed item: restrict C-style casts to explicit `unsafe` regions.
- What changed:
  - semantic cast handling now rejects C-style casts in cNxt mode.
  - added dedicated cNxt Sema diagnostic for unsupported non-declaration features.
  - extended `clang/test/Parser/cnxt-restrictions.cpp` with C-style cast rejection coverage.
- What is now unblocked:
  - M2-13 include-flow policy enforcement is independent and ready.
  - M2-14 recovery tests can include cast-restriction scenarios.
- Direction check:
  - roadmap remains directionally correct; this reduces unsafe C++ escape hatches in cNxt.

### 2026-03-15 - M2-13

- Completed item: reject textual include-based cNxt package flows.
- What changed:
  - preprocessor include handling now emits a cNxt policy error for textual include directives.
  - include directive is discarded after the diagnostic to keep parsing stable.
  - added `clang/test/Preprocessor/cnxt-no-include.c` coverage.
- What is now unblocked:
  - M2-14 can consolidate and harden recovery-oriented restriction tests as the final milestone-2 item.
- Direction check:
  - roadmap remains directionally correct; this reinforces module/import-first cNxt package flow.

### 2026-03-15 - M2-14

- Completed item: add recovery-focused tests for remaining milestone-2 restrictions.
- What changed:
  - added parser recovery coverage in `clang/test/Parser/cnxt-recovery.cpp` spanning template, inheritance, operator-overload, and cast restrictions.
  - extended `clang/test/Preprocessor/cnxt-no-include.c` so verification requires post-include parsing to continue.
- What is now unblocked:
  - milestone 2 is complete; milestone 3 ownership feasibility and vocabulary work can begin.
- Direction check:
  - roadmap remains directionally correct; restriction enforcement now has explicit recovery regression coverage.

### 2026-03-15 - M3-00

- Completed item: feasibility spike for std-backed ownership handles without user memory headers.
- What changed:
  - added `cnxt/docs/m3-00-feasibility.md` with experiment matrix and concrete outcomes.
  - documented current blockers and fallback constraints.
- What is now unblocked:
  - M3-01 ownership vocabulary standardization with evidence-backed assumptions.
  - M3-02 parser/type work for ownership handle spellings.
  - M3-03 prelude/module design with explicit constraints from measured behavior.
- Direction check:
  - roadmap remains directionally correct; the spike confirms feasibility direction but highlights required compiler-owned boundaries.

### 2026-03-15 - M3-01

- Completed item: standardize ownership vocabulary on `unique/shared/weak`.
- What changed:
  - updated `cnxt/README.md` ownership model and roadmap references from `strong` to `unique`.
  - updated milestone-2 scope text to reference `unique<T>` instead of `strong<T>`.
- What is now unblocked:
  - M3-02 parser/type work can target stable ownership spellings.
  - M3-03 prelude design can expose finalized user-facing handle names.
- Direction check:
  - roadmap remains directionally correct; docs now match intended ownership vocabulary.

### 2026-03-15 - M3-02

- Completed item: parse and type-check cNxt ownership handles `unique<T>`, `shared<T>`, and `weak<T>`.
- What changed:
  - parser now treats `unique/shared/weak` template-id spellings as cNxt ownership-handle exceptions instead of generic forbidden template argument lists.
  - compiler-provided ownership-handle declarations were introduced so cNxt handle spellings can type-check without user-authored templates.
  - added parser coverage in `clang/test/Parser/cnxt-ownership.cpp` for accepted handles while preserving rejection of non-handle template-ids and template declarations.
- What is now unblocked:
  - M3-03 can focus on shaping the compiler-owned prelude/injection boundary rather than basic handle name recognition.
  - M3-04 and M3-05 lowering work can target already-parsed and typed handle surfaces.
- Direction check:
  - roadmap remains directionally correct; cNxt now has a compiler-owned ownership type surface while keeping the broader template restrictions in place.

### 2026-03-15 - M3-03

- Completed item: add compiler-owned cNxt prelude/injected ownership declarations.
- What changed:
  - frontend preprocessor initialization now injects a dedicated `<cnxt-prelude>` block that declares `unique<T>`, `shared<T>`, and `weak<T>`.
  - cNxt template-declaration restriction now exempts compiler-prelude locations while preserving user-file template rejection.
  - moved ownership declaration injection out of Sema initialization and into the preprocessor prelude path.
  - added preprocessor coverage in `clang/test/Preprocessor/cnxt-prelude.c` and kept parser restriction coverage green.
- What is now unblocked:
  - M3-04 can lower `unique<T>` with a stable compiler-owned declaration boundary.
  - M3-05 and M3-06 lowering can reuse the same prelude injection mechanism.
- Direction check:
  - roadmap remains directionally correct; ownership handles are now provided through an explicit compiler-owned prelude path rather than ad hoc declaration injection.

### 2026-03-15 - M3-04

- Completed item: lower `unique<T>` to an internal std-backed representation.
- What changed:
  - cNxt prelude now maps `unique<T>` to `std::unique_ptr<T>`.
  - prelude uses `#if __has_include(<memory>)` to prefer real `<memory>` when available and provides a minimal internal `std::unique_ptr` fallback when it is not.
  - template/include cNxt restrictions were tightened to still reject user-source forms while allowing compiler-prelude and system-header processing needed for internal lowering.
  - added parser coverage in `clang/test/Parser/cnxt-unique-lowering.cpp` and updated prelude coverage in `clang/test/Preprocessor/cnxt-prelude.c`.
- What is now unblocked:
  - M3-05 and M3-06 can mirror this pattern for `shared<T>` and `weak<T>`.
  - M3-07 can build on `unique<T>` now being represented as `std::unique_ptr` at the language boundary.
- Direction check:
  - roadmap remains directionally correct; `unique<T>` now has a concrete std-oriented lowering path while preserving no-header requirements for user source.

### 2026-03-15 - M3-05

- Completed item: lower `shared<T>` to an internal std-backed representation.
- What changed:
  - cNxt prelude now maps `shared<T>` to `std::shared_ptr<T>`.
  - internal fallback path now provides a minimal `std::shared_ptr` shape when `<memory>` is unavailable.
  - added parser coverage in `clang/test/Parser/cnxt-shared-lowering.cpp` and updated prelude coverage in `clang/test/Preprocessor/cnxt-prelude.c`.
- What is now unblocked:
  - M3-06 can align `weak<T>` to the same std-backed/fallback prelude strategy.
  - M3-08 can enforce `shared<T>` copy/reference-count semantics on top of the stabilized representation.
- Direction check:
  - roadmap remains directionally correct; both `unique<T>` and `shared<T>` now lower through the same compiler-owned std-oriented prelude boundary.

### 2026-03-15 - M3-06

- Completed item: lower `weak<T>` to an internal std-backed representation.
- What changed:
  - cNxt prelude now maps `weak<T>` to `std::weak_ptr<T>`.
  - internal fallback path now provides a minimal `std::weak_ptr` shape with `lock()` and `expired()` when `<memory>` is unavailable.
  - added parser coverage in `clang/test/Parser/cnxt-weak-lowering.cpp` and updated prelude coverage in `clang/test/Preprocessor/cnxt-prelude.c`.
- What is now unblocked:
  - M3-07/M3-08/M3-09 can now enforce ownership semantics on top of a complete `unique/shared/weak` lowered surface.
- Direction check:
  - roadmap remains directionally correct; all three ownership handle spellings now flow through the same compiler-owned std-oriented lowering boundary.

### 2026-03-15 - M3-07

- Completed item: enforce move-only semantics for `unique<T>`.
- What changed:
  - fallback `std::unique_ptr` in the cNxt prelude now explicitly deletes copy construction/assignment and permits moves.
  - cNxt operator-overload restriction now remains enforced for user code while exempting system-header declarations needed by compiler/runtime-provided ownership internals.
  - added parser/semantic coverage in `clang/test/Parser/cnxt-unique-move-only.cpp`.
- What is now unblocked:
  - M3-08 can focus on `shared<T>` copy/reference semantics without ambiguity around unique ownership copying.
  - M3-09 can rely on a distinct move-only `unique<T>` source when validating weak upgrade/deref rules.
- Direction check:
  - roadmap remains directionally correct; unique ownership now has explicit non-copyable semantics in no-`<memory>` fallback builds while preserving the restricted user surface.

### 2026-03-15 - M3-08

- Completed item: enforce reference-count semantics and copy rules for `shared<T>`.
- What changed:
  - fallback `std::shared_ptr` in the cNxt prelude now has explicit copy/move special member behavior declarations (copyable by design).
  - added parser/semantic coverage in `clang/test/Parser/cnxt-shared-copy-rules.cpp`.
- What is now unblocked:
  - M3-09 can enforce weak upgrade/deref behavior against a stable, explicitly copyable shared-handle surface.
  - M3-10 can add ownership-conversion diagnostics with clearer baseline handle copy/move rules.
- Direction check:
  - roadmap remains directionally correct; shared ownership copy semantics are now explicit in fallback builds while std-backed behavior remains primary when `<memory>` is present.

### 2026-03-15 - M3-09

- Completed item: enforce weak-handle lock-before-use access rules.
- What changed:
  - fallback `std::weak_ptr` in the cNxt prelude now hides raw storage and exposes lock/expired accessors, reducing direct raw-handle access.
  - added parser/semantic coverage in `clang/test/Parser/cnxt-weak-lock-required.cpp` to require lock-style access.
- What is now unblocked:
  - M3-10 can add explicit ownership-conversion diagnostics on top of stable unique/shared/weak access patterns.
  - M3-12 baseline ownership behavior tests can rely on lock-before-use regression coverage.
- Direction check:
  - roadmap remains directionally correct; weak-handle usage now emphasizes lock/upgrade access paths across both std-backed and fallback representations.

### 2026-03-15 - M3-10

- Completed item: add diagnostics for illegal ownership conversions in cNxt assignment flows.
- What changed:
  - added a dedicated cNxt Sema diagnostic for illegal ownership-handle conversion direction (`unique -> shared -> weak` is the only widening path).
  - added ownership-kind classification and conversion-flow checks in semantic assignment handling, including overloaded assignment paths, so rejected flows report cNxt-specific diagnostics instead of generic overload failures.
  - extended cNxt parser/semantic coverage in `clang/test/Parser/cnxt-ownership-conversions.cpp`.
- What is now unblocked:
  - M3-11 can focus on unsafe FFI raw-pointer boundary rules without ambiguity in ownership-handle conversion diagnostics.
  - M3-12 baseline ownership test expansion can now assert explicit illegal-conversion diagnostics.
- Direction check:
  - roadmap remains directionally correct; ownership-handle semantics now expose explicit language-level diagnostics for illegal conversion direction.

### 2026-03-15 - M3-11

- Completed item: add raw-pointer FFI boundary rules for cNxt.
- What changed:
  - semantic declaration checks now reject raw pointer declarations in cNxt user code for variables and fields.
  - cNxt function declarations now reject raw pointer signatures unless the declaration is `extern "C"` (FFI boundary).
  - added parser/semantic coverage in `clang/test/Parser/cnxt-ffi-raw-pointers.cpp` for rejected global/local/field/function-pointer forms and accepted `extern "C"` pointer signatures.
- What is now unblocked:
  - M3-12 can consolidate ownership baseline tests with explicit raw-pointer boundary enforcement coverage.
  - M3-13 interoperability tests can assume explicit `extern "C"` pointer-boundary behavior in cNxt mode.
- Direction check:
  - roadmap remains directionally correct; cNxt now enforces a concrete raw-pointer policy tied to explicit FFI boundaries.

### 2026-03-15 - M3-12

- Completed item: add parser/sema/codegen baseline ownership tests.
- What changed:
  - added parser baseline coverage in `clang/test/Parser/cnxt-ownership-baseline.cpp` for accepted ownership-handle surface operations.
  - added sema baseline coverage in `clang/test/SemaCXX/cnxt-ownership-baseline.cpp` for illegal ownership conversion diagnostics and weak-lock flow typing.
  - added codegen baseline coverage in `clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp` to verify std-backed ownership handle lowering and weak lock/expired call emission in LLVM IR.
- What is now unblocked:
  - M3-13 can focus on mixed cNxt/C++ ABI interoperability with baseline parser/sema/codegen ownership regressions already covered.
- Direction check:
  - roadmap remains directionally correct; ownership milestone confidence is now anchored by dedicated parser, sema, and codegen regression tests.

### 2026-03-15 - M3-13

- Completed item: add mixed cNxt/C++ ABI interoperability coverage.
- What changed:
  - added `clang/test/CodeGenCXX/cnxt-ownership-interop.cpp` with split-file cNxt and C++ translation units.
  - verified cNxt-side IR emission for extern-C ownership-handle and raw-pointer boundary functions.
  - verified C++-side IR declarations/calls use ABI-compatible signatures when calling cNxt extern-C entry points.
- What is now unblocked:
  - milestone 3 is complete; milestone 4 package-manager implementation can start on top of a tested ownership baseline and interop boundary.
- Direction check:
  - roadmap remains directionally correct; ownership runtime work now has cross-language ABI coverage in addition to parser/sema/codegen unit regression tests.

### 2026-03-15 - M4-01

- Completed item: define `Cnxt.toml` manifest schema and validation rules.
- What changed:
  - added `cnxt/specs/cnxt-manifest-schema.md` as the schema source-of-truth for manifest versioning, package metadata, dependency specification forms, target declarations, profiles, and workspace metadata.
  - documented explicit validation constraints and baseline diagnostic IDs (`CNXT1001` through `CNXT1008`) for parser/validator implementation in the next deliverables.
  - linked the schema spec from `cnxt/README.md` in the package-layout section.
- What is now unblocked:
  - M4-02 can implement a parser that validates against a concrete key/type/value contract instead of inferred conventions.
  - M4-03 and M4-04 can build on standardized dependency/source/path semantics and error taxonomy.
- Direction check:
  - roadmap remains directionally correct; milestone 4 now has a concrete manifest contract suitable for incremental parser and resolver implementation.

### 2026-03-15 - M4-02

- Completed item: implement manifest parser with structured diagnostics.
- What changed:
  - added `cnxt/tools/manifest_parser.py` with schema-aware `Cnxt.toml` parsing and validation, including structured diagnostics (`CNXT1001` to `CNXT1008`).
  - implemented a Python 3.11 `tomllib` path and a Python 3.8-compatible minimal TOML parser fallback so parser behavior is stable in this repository environment.
  - added unit coverage in `cnxt/tools/tests/test_manifest_parser.py` for valid manifests, missing/unknown keys, manifest-version checks, dependency source constraints, path escape checks, and structured parse errors.
- What is now unblocked:
  - M4-03 can consume validated manifest objects with normalized schema assumptions and deterministic diagnostic IDs.
  - M4-04 can build constraint solving directly on validated dependency specs (`version`, `path`, `git`) without re-implementing schema checks.
- Direction check:
  - roadmap remains directionally correct; milestone 4 now has executable schema enforcement with test-backed diagnostics as a base for graph and solver work.

### 2026-03-15 - M4-03

- Completed item: implement dependency graph construction and cycle diagnostics.
- What changed:
  - added `cnxt/tools/dependency_graph.py` to build local path-dependency graphs from validated manifests.
  - implemented graph diagnostics for manifest-parse failures, missing path-dependency manifests, duplicate package names, and dependency cycles (`CNXT2001`-`CNXT2004`).
  - added unit coverage in `cnxt/tools/tests/test_dependency_graph.py` for acyclic graphs, missing-path diagnostics, duplicate-name diagnostics, and cycle detection.
- What is now unblocked:
  - M4-04 can perform version-constraint solving on top of a resolved graph shape and package identity map.
  - M4-05 lockfile work can target deterministic graph outputs with explicit cycle/missing-node failure behavior.
- Direction check:
  - roadmap remains directionally correct; milestone 4 now has parser + graph foundations with structured diagnostics for topology errors.

### 2026-03-15 - M4-04

- Completed item: implement version constraint solving.
- What changed:
  - added `cnxt/tools/version_solver.py` to solve manifest dependency requirements and emit structured diagnostics (`CNXT3001`-`CNXT3003`).
  - implemented semver requirement parsing/intersection for exact, comparator, caret, and tilde constraints.
  - added unit coverage in `cnxt/tools/tests/test_version_solver.py` for compatible intersections, conflicting constraints, unsupported requirements, local-version mismatch diagnostics, and caret behavior for `0.x.y`.
- What is now unblocked:
  - M4-05 can consume deterministic solved constraints when generating lockfiles.
  - M4-07 package fetching can rely on already-detected version conflicts/invalid constraints before network resolution.
- Direction check:
  - roadmap remains directionally correct; package-manager flow now has parser, graph, and solver layers with test-backed diagnostics.

### 2026-03-15 - M4-05

- Completed item: implement lockfile format and deterministic lockfile generation.
- What changed:
  - added `cnxt/specs/cnxt-lockfile-schema.md` defining `Cnxt.lock` v1 shape and determinism rules.
  - added `cnxt/tools/lockfile_generator.py` with deterministic lockfile generation, rendering, and file writing (`Cnxt.lock` default output).
  - added unit coverage in `cnxt/tools/tests/test_lockfile_generator.py` for deterministic generation, conflict-failure handling, and default output path writing.
  - linked lockfile spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-06 can lay out cache paths using deterministic lockfile package entries.
  - M4-08/M4-09/M4-10 command work can consume lockfile outputs instead of ad hoc resolution state.
- Direction check:
  - roadmap remains directionally correct; package-manager flow now includes a stable lock artifact between solving and fetch/build steps.

### 2026-03-15 - M4-06

- Completed item: implement local cache layout for downloaded packages.
- What changed:
  - added `cnxt/specs/cnxt-cache-layout.md` defining cache root, directory structure, keying rules, and planning behavior.
  - added `cnxt/tools/cache_layout.py` with deterministic cache root/layout computation, directory initialization, and lockfile-driven cache-entry planning for registry and git dependencies.
  - added structured cache diagnostics (`CNXT5001`-`CNXT5003`) for lockfile loading/validation failures.
  - added unit coverage in `cnxt/tools/tests/test_cache_layout.py` for layout initialization, deterministic keying, lockfile entry planning, and invalid lockfile diagnostics.
  - linked cache layout spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-07 fetcher implementation can use stable cache paths/keys instead of inventing storage conventions.
  - M4-08/M4-10 command work can initialize/cache-plan before invoking download/build steps.
- Direction check:
  - roadmap remains directionally correct; package-manager pipeline now has deterministic manifests -> graph -> solver -> lockfile -> cache-layout staging.

### 2026-03-15 - M4-07

- Completed item: implement package fetcher (registry and git source support).
- What changed:
  - added `cnxt/specs/cnxt-fetcher-sources.md` defining baseline registry index format, version selection behavior, and git source handling.
  - added `cnxt/tools/package_fetcher.py` to fetch lockfile dependencies into cache for both `version` and `git` sources.
  - implemented registry index loading + highest-satisfying-version selection and git mirror/checkout flows.
  - added fetch diagnostics (`CNXT6003`-`CNXT6005`) and structured fetch records for fetched/cached outcomes.
  - added unit coverage in `cnxt/tools/tests/test_package_fetcher.py` for registry + git fetch success, missing registry index failure, and cache-hit behavior on repeated fetch.
  - linked fetcher source spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-08 build command can run lockfile+fetch pipeline with concrete cached inputs.
  - M4-09/M4-10 command work can reuse the same fetch stage before compile/test orchestration.
- Direction check:
  - roadmap remains directionally correct; package-manager foundations now include parsing, solving, locking, cache layout, and source fetching.

### 2026-03-15 - M4-08

- Completed item: implement `cnxt build` command.
- What changed:
  - added `cnxt/tools/cnxt_build.py` to orchestrate manifest validation, lockfile generation, optional dependency fetch, target derivation, compile-command emission, and compile/link execution.
  - implemented `debug`/`release` profile flags and default target discovery (`src/main.cn`, `src/lib.cn`) with explicit `[targets]` support.
  - emits deterministic `compile_commands.json` for derived compile steps.
  - added build diagnostics (`CNXT7001`-`CNXT7004`) for lock/target/command failure scenarios.
  - added `cnxt/specs/cnxt-build-command.md` documenting baseline workflow and diagnostics.
  - added unit coverage in `cnxt/tools/tests/test_cnxt_build.py` for dry-run planning, missing-target failure, and executable build path with a mock compiler.
  - linked build-command spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-09 can reuse build orchestration to run built binaries.
  - M4-10 can reuse build orchestration for test target execution.
- Direction check:
  - roadmap remains directionally correct; package-manager implementation now has a concrete build entry point on top of lock+fetch primitives.

### 2026-03-15 - M4-09

- Completed item: implement `cnxt run` command.
- What changed:
  - added `cnxt/tools/cnxt_run.py` to build-or-reuse artifacts, select binary targets, execute binaries, and return structured run outputs.
  - implemented `--skip-build`, `--bin`, profile selection, and argument forwarding support.
  - added run diagnostics (`CNXT7101`-`CNXT7104`) for binary selection and runtime-failure paths.
  - added `cnxt/specs/cnxt-run-command.md` documenting baseline run workflow and diagnostics.
  - added unit coverage in `cnxt/tools/tests/test_cnxt_run.py` for build+run integration, missing binary handling, and named-binary selection behavior.
  - linked run-command spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-10 can reuse build and runtime execution paths to implement test command behavior.
  - M4-11 workspace discovery can be integrated once run/test command entry points are stable.
- Direction check:
  - roadmap remains directionally correct; command surface now includes build and run baselines backed by lock/fetch/cache plumbing.

### 2026-03-15 - M4-10

- Completed item: implement `cnxt test` command.
- What changed:
  - added `cnxt/tools/cnxt_test.py` to build-or-reuse test artifacts and execute test binaries with structured per-test results.
  - implemented test filtering, skip-build mode, and build/fetch integration via existing command pipeline.
  - added test diagnostics (`CNXT7201`-`CNXT7203`) for no-tests, missing binaries, and failing test executions.
  - added `cnxt/specs/cnxt-test-command.md` documenting baseline `cnxt test` behavior.
  - added unit coverage in `cnxt/tools/tests/test_cnxt_test.py` for pass/fail/no-test scenarios.
  - linked test-command spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-11 workspace/project-root discovery can now be wired across build/run/test command entry points.
  - M4-12 and M4-13 E2E command tests can target stable build/run/test command surfaces.
- Direction check:
  - roadmap remains directionally correct; milestone 4 now has baseline command coverage for build/run/test on top of lock/fetch/cache foundations.

### 2026-03-15 - M4-11

- Completed item: implement workspace/project-root discovery behavior.
- What changed:
  - added `cnxt/tools/workspace_discovery.py` with upward manifest search, workspace-root/member resolution, and structured discovery diagnostics (`CNXT8001`, `CNXT8002`).
  - integrated discovery into `cnxt_build.py`, `cnxt_run.py`, and `cnxt_test.py` so commands accept manifest files, project directories, or current-directory defaults.
  - added `cnxt/specs/cnxt-workspace-discovery.md` documenting resolution rules and command integration.
  - added unit coverage in `cnxt/tools/tests/test_workspace_discovery.py` for workspace-member resolution, missing-manifest errors, and command integration from directory input.
  - linked workspace discovery spec from `cnxt/README.md`.
- What is now unblocked:
  - M4-12 and M4-13 end-to-end test suites can now exercise command flows from workspace/member working directories.
  - M4-14 reproducibility testing can run through stable command entry-point resolution logic.
- Direction check:
  - roadmap remains directionally correct; milestone 4 command ergonomics now include explicit project/workspace discovery behavior.

### 2026-03-15 - M4-12

- Completed item: add end-to-end tests for local path dependencies.
- What changed:
  - added `cnxt/tools/tests/test_e2e_local_path_dependencies.py` covering integrated local path dependency flows.
  - test coverage now exercises build/run/test command pipeline over local path package graphs, including lockfile generation and directory-input command invocation.
  - E2E fixtures include workspace/member layouts and local path dependency manifests validated through command execution with mock compiler outputs.
- What is now unblocked:
  - M4-13 registry E2E tests can reuse the same end-to-end harness structure for non-local sources.
  - M4-14 reproducibility checks can build on existing E2E command scaffolding.
- Direction check:
  - roadmap remains directionally correct; local path dependency behavior is now covered with command-level integration tests rather than only unit slices.

### 2026-03-15 - M4-13

- Completed item: add end-to-end tests for registry dependencies.
- What changed:
  - added `cnxt/tools/tests/test_e2e_registry_dependencies.py` for registry-backed command-level integration coverage.
  - E2E tests now validate build/run/test pipeline behavior with registry dependency resolution and cache population.
  - added negative-path coverage where unsatisfied registry requirements fail builds with the expected diagnostic flow.
- What is now unblocked:
  - M4-14 reproducibility tests can now reuse both local-path and registry E2E fixtures.
  - milestone 4 closure work can focus on deterministic replay guarantees rather than missing source-mode coverage.
- Direction check:
  - roadmap remains directionally correct; milestone 4 now has end-to-end coverage for both local path and registry dependency modes.

### 2026-03-15 - M4-14

- Completed item: add reproducibility tests for lockfile replay in CI.
- What changed:
  - added lock replay E2E coverage in `cnxt/tools/tests/test_e2e_lockfile_replay.py` validating deterministic locked rebuilds.
  - build pipeline now supports `--locked`/locked mode to replay existing lockfiles without regeneration.
  - fetch pipeline now honors lockfile `resolved-version` pins for version-source dependencies.
  - build pipeline persists fetched resolved versions back into lockfile dependency entries to enable deterministic replay.
  - updated lockfile/build/fetch specs to document pinned-version replay behavior and locked build diagnostics.
- What is now unblocked:
  - milestone 4 is complete; milestone 5 IDE-quality deliverables can proceed on top of a test-backed package-manager command pipeline.
- Direction check:
  - roadmap remains directionally correct; package-manager foundation now includes deterministic lockfile replay guarantees suitable for CI reproducibility checks.

### 2026-03-15 - M5-01

- Completed item: ensure clangd fallback compile commands select cNxt mode.
- What changed:
  - updated `clang-tools-extra/clangd/GlobalCompilationDatabase.cpp` fallback command generation so `.cn`, `.cnxt`, and `.cni` files get `-x cnxt`.
  - extended `clang-tools-extra/clangd/unittests/GlobalCompilationDatabaseTests.cpp` fallback command assertions to cover cNxt file extensions.
- What is now unblocked:
  - M5-02 completion-quality work can assume cNxt files opened without a compile database start in the right language mode.
  - M5-03 and M5-04 IDE behavior tests can rely on consistent fallback parsing mode for cNxt extensions.
- Direction check:
  - roadmap remains directionally correct; fallback compile command language selection now aligns with cNxt file extensions.

### 2026-03-15 - M5-02

- Completed item: improve completion ranking for cNxt-first constructs and restrictions.
- What changed:
  - updated `clang-tools-extra/clangd/CodeComplete.cpp` scoring flow to detect cNxt files by extension.
  - added cNxt completion score boosts for cNxt-first constructs (`fn`, `let`, `var`, `import`, `unsafe`, `unique`, `shared`, `weak`).
  - added cNxt completion score penalties for restricted C++ constructs (`template`, `try`, `catch`, `throw`, `goto`, `new`, `delete`).
  - added `clang-tools-extra/clangd/unittests/CodeCompleteTests.cpp` regression coverage (`CNxtRankingAdjustments`) asserting preferred cNxt completions rank above restricted constructs.
- What is now unblocked:
  - M5-03 semantic token coverage can build on improved cNxt completion behavior.
  - M5-04 and M5-05 IDE regression work can assume cNxt restriction-aware completion ordering.
- Direction check:
  - roadmap remains directionally correct; cNxt IDE defaults now bias toward language-first constructs and away from restricted C++ surfaces.

### 2026-03-15 - M5-03

- Completed item: add semantic token classification coverage for cNxt files.
- What changed:
  - extended `clang-tools-extra/clangd/unittests/SemanticHighlightingTests.cpp` with `CNxtFileCoverage`.
  - new test builds ASTs for `.cn` and `.cnxt` files in cNxt mode and verifies semantic token annotations include expected class/function highlights.
- What is now unblocked:
  - M5-04 go-to-definition/reference regression work can build on explicit cNxt semantic token baseline coverage.
  - M5-05 refactor-safety checks can assume cNxt semantic-highlighting pipeline remains exercised in tests.
- Direction check:
  - roadmap remains directionally correct; cNxt IDE tokenization now has dedicated regression coverage for cNxt file extensions.

### 2026-03-15 - M5-04

- Completed item: add go-to-definition/reference regression tests for cNxt sources.
- What changed:
  - extended `clang-tools-extra/clangd/unittests/XRefsTests.cpp` with `LocateSymbol.CNxtFile`.
  - added `FindReferences.CNxtWithinAST` coverage plus a cNxt-specific reference harness that builds `.cn` files with `-x cnxt -std=cnxt1`.
- What is now unblocked:
  - M5-05 refactor-safety checks can build on explicit cNxt xrefs regression coverage.
  - M5-09 IDE integration CI can include cNxt xrefs expectations as part of representative project validation.
- Direction check:
  - roadmap remains directionally correct; cNxt navigation behavior now has dedicated locate/reference regression tests.

### 2026-03-15 - M5-05

- Completed item: add refactor safety checks for restricted constructs.
- What changed:
  - updated `clang-tools-extra/clangd/refactor/Tweak.cpp` with a cNxt-only safety guard that suppresses tweak preparation when the active selection/cursor touches restricted constructs (`goto`, `do`, `try/catch/throw`, `new/delete`, `template`, `#include`, and C-style `for(...)` patterns).
  - extended `clang-tools-extra/clangd/unittests/tweaks/AnnotateHighlightingsTests.cpp` with cNxt regression coverage proving allowed code remains tweakable while restricted constructs are unavailable.
- What is now unblocked:
  - M5-06 formatter profile work can proceed with refactor actions now explicitly guarded around banned constructs.
  - M5-08 fix-it work can target restricted diagnostics with less risk of conflicting refactor suggestions in the same regions.
- Direction check:
  - roadmap remains directionally correct; cNxt IDE refactor behavior now has an explicit safety boundary for restricted language surface.

### 2026-03-15 - M5-06

- Completed item: implement cNxt formatter baseline profile.
- What changed:
  - added `cnxt/tools/cnxt_format.py` with a single baseline profile, clang-format invocation, check/write modes, and structured diagnostics (`CNXT9001`-`CNXT9005`).
  - added formatter unit coverage in `cnxt/tools/tests/test_cnxt_format.py`.
  - added formatter profile spec `cnxt/specs/cnxt-formatter-profile.md` and linked it from `cnxt/README.md`.
- What is now unblocked:
  - M5-07 lint rules can align messaging and policy checks against a stable formatter baseline.
  - M5-09 CI integration can validate formatting alongside clangd behavior and package-manager workflows.
- Direction check:
  - roadmap remains directionally correct; cNxt tooling now has a deterministic formatter baseline with test-backed behavior.

### 2026-03-15 - M5-07

- Completed item: add one-obvious-way policy lints for cNxt source.
- What changed:
  - added `cnxt/tools/cnxt_lint.py` with deterministic line/column diagnostics and comment/string masking.
  - added baseline lint rules for textual include, C-style `for(...)`, manual heap operators, exception constructs, and template declarations (`CNXT9101`-`CNXT9105`), plus input-path diagnostics (`CNXT9100`).
  - added unit coverage in `cnxt/tools/tests/test_cnxt_lint.py`.
  - added lint-policy spec `cnxt/specs/cnxt-lint-policy.md` and linked it from `cnxt/README.md`.
- What is now unblocked:
  - M5-08 fix-it support can attach safe transformations to existing stable lint/diagnostic surfaces.
  - M5-09 CI integration can run formatter+linter baselines as part of IDE-quality checks.
- Direction check:
  - roadmap remains directionally correct; cNxt guardrail tooling now includes explicit lint policies with test-backed diagnostics.

### 2026-03-15 - M5-08

- Completed item: add safe fix-its for common cNxt restriction diagnostics.
- What changed:
  - extended `cnxt/tools/cnxt_lint.py` diagnostics with optional `fix` payloads and added `--apply-fixes` mode.
  - implemented safe v1 fix-it for quoted textual includes (`#include "x"` -> `import "x";`) and post-fix re-linting.
  - added fix-it regression coverage in `cnxt/tools/tests/test_cnxt_lint.py`.
  - added fix-it spec `cnxt/specs/cnxt-fixits.md` and linked fix-it guidance from `cnxt/specs/cnxt-lint-policy.md` and `cnxt/README.md`.
- What is now unblocked:
  - M5-09 CI integration can now validate formatter, lints, and safe fix-it behavior for representative cNxt projects.
- Direction check:
  - roadmap remains directionally correct; IDE guardrails now include both diagnostics and safe automated remediation for common cases.

### 2026-03-15 - M5-09

- Completed item: add IDE integration tests to CI with representative cNxt projects.
- What changed:
  - added CI workflow `.github/workflows/cnxt-ide-integration.yml` running IDE-focused cNxt tool tests on Python 3.8 and 3.11.
  - added representative IDE E2E coverage in `cnxt/tools/tests/test_e2e_ide_workflows.py` for format + lint fix-it + compile database flow and workspace-member build entrypoints.
  - added CI integration spec `cnxt/specs/cnxt-ide-ci.md` and linked it from `cnxt/README.md`.
- What is now unblocked:
  - milestone 5 is complete.
  - roadmap can transition to post-M5 hardening and expansion tasks.
- Direction check:
  - roadmap remains directionally correct; cNxt IDE-quality work now includes regression-tested local tooling and CI enforcement for representative project flows.
