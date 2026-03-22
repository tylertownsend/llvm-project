# SESSION_LOG

## 2026-03-21

- Completed `M10-01`.
- Extended `cnxt/runtime/ownership/tests/ownership_runtime_smoke.cpp` with
  `use_after_free` and `weak_lock_stress` modes so the sanitizer harness now
  covers leak, use-after-free, double-free, and concurrent weak-lock stress.
- Updated `cnxt/runtime/ownership/CMakeLists.txt` so `ctest` runs the new
  clean stress case and the new sanitizer-enforced UAF failure case.
- Updated `cnxt/runtime/ownership/README.md` with the sanitizer/stress
  invocation used by the ownership-runtime job.
- Validation:
  - `cmake -S cnxt/runtime/ownership -B /tmp/cnxt-ownership-stress -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_CXX_COMPILER=c++ -DBUILD_TESTING=ON -DCNXT_OWNERSHIP_RT_ENABLE_SANITIZERS=ON`
  - `cmake --build /tmp/cnxt-ownership-stress --parallel`
  - `ctest --test-dir /tmp/cnxt-ownership-stress --output-on-failure`
  - `git diff --check`
- Next target: `M10-02`.

- Completed `M9-08`.
- Taught `cnxt/tools/cnxt_build.py` to auto-stage the ownership runtime,
  inject `-fcnxt-ownership-runtime=...`, and link cNxt binaries/tests with an
  `$ORIGIN` rpath so starter-layout projects run without manual runtime flags
  or `LD_LIBRARY_PATH`.
- Added the starter-layout fixture at `cnxt/examples/starter/hello-app/` and a
  real end-to-end tool test in `cnxt/tools/tests/test_e2e_starter_template.py`
  proving the template builds and runs with no user-written FFI glue.
- Updated package-tool defaults/docs/tests so `cnxt build` / `cnxt run` now
  reflect the no-glue starter path.
- Validation:
  - `python3 cnxt/tools/tests/test_cnxt_build.py`
  - `python3 cnxt/tools/tests/test_cnxt_run.py`
  - `python3 cnxt/tools/tests/test_cnxt_test.py`
  - `python3 cnxt/tools/tests/test_e2e_ide_workflows.py`
  - `python3 cnxt/tools/tests/test_e2e_starter_template.py`
  - `git diff --check`
- Next target: `M10-01`.

- Completed `M9-07`.
- Added `cnxt/docs/c-abi-migration.md`, a migration guide covering when to
  replace manual `extern "C"` imports/exports with `cnxt_import_c` /
  `cnxt_export_c` and when to keep `unsafe extern "C"` for raw-pointer FFI.
- Linked the guide from `cnxt/README.md` and `cnxt/specs/cnxt-ffi-boundary.md`
  so the branch documentation points at one migration source of truth.
- Validation:
  - `build/bin/llvm-lit -sv clang/test/Driver/cnxt-c-abi-mixed-interop.c`
  - `git diff --check`
- Next target: `M9-08`.

- Completed `M9-06`.
- Added `clang/test/Driver/cnxt-c-abi-mixed-interop.c`, a split-file
  build-and-run test that links one cNxt file with separate C and C++
  translation units through `cnxt_import_c` / `cnxt_export_c`.
- The new executable validates cNxt importing C and C++ symbols plus C and
  C++ callers invoking cNxt-exported symbols, then prints a success message.
- Validation:
  - `build/bin/llvm-lit -sv clang/test/Driver/cnxt-c-abi-mixed-interop.c`
- Next target: `M9-07`.

- Completed `M9-05`.
- Aligned cNxt raw-pointer diagnostics so `cnxt_import_c` / `cnxt_export_c`
  are explicitly described as ownership-handle ABI surfaces, with guidance
  that raw-pointer FFI still belongs under `unsafe extern "C"`.
- Added parser coverage in `clang/test/Parser/cnxt-ffi-raw-pointers.cpp` and a
  focused sema guidance test in
  `clang/test/SemaCXX/cnxt-c-abi-pointer-guidance.cpp`.
- Updated `clang/test/SemaCXX/cnxt-pointer-guidance-fixits.cpp` so the
  existing `unsafe extern "C"` fix-it coverage tracks the current diagnostic
  ordering.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/Parser/cnxt-ffi-raw-pointers.cpp clang/test/SemaCXX/cnxt-c-abi-pointer-guidance.cpp clang/test/SemaCXX/cnxt-pointer-guidance-fixits.cpp clang/test/SemaCXX/cnxt-ownership-escapes.cpp`
  - `git diff --check`
- Next target: `M9-06`.

- Completed `M9-04`.
- Added ownership-handle marshalling rules to
  `cnxt/specs/cnxt-ffi-boundary.md`, defining how `unique/shared/weak`
  preserve move/copy/weak-observer semantics across `cnxt_export_c` /
  `cnxt_import_c` instead of being rewritten into raw-pointer adapters.
- Added `clang/test/CodeGenCXX/cnxt-c-abi-ownership-marshalling.cpp` to cover
  exported handle signatures, imported handle calls, unique move transfer,
  shared/weak copy semantics, and runtime-backed `weak.lock()` on the
  compiler-managed C symbol surface.
- Validation:
  - `build/bin/llvm-lit -sv clang/test/CodeGenCXX/cnxt-c-abi-ownership-marshalling.cpp clang/test/CodeGenCXX/cnxt-c-abi-thunks.cpp clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp`
  - `git diff --check`
- Next target: `M9-05`.

- Completed `M9-03`.
- Added `cnxt_export_c` / `cnxt_import_c` to the injected cNxt prelude and
  taught `SemaDecl.cpp` to lower those annotations on free functions to
  unmangled C symbol names, removing the need for user-written wrapper bodies
  when importing/exporting cNxt functions through the C ABI.
- Added `clang/test/CodeGenCXX/cnxt-c-abi-thunks.cpp` and updated
  `cnxt/README.md` to document the new wrapper-free import/export surface.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/CodeGenCXX/cnxt-c-abi-thunks.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp clang/test/Preprocessor/cnxt-prelude.c`
  - `git diff --check`
- Next target: `M9-04`.

- Completed `M9-02`.
- Added a compiler-owned `cnxt::io::println(...)` prelude surface in
  `InitPreprocessor.cpp`, plus a hello-world example at
  `cnxt/examples/stdlib/hello-world.cn` and a driver test that builds and runs
  it without any user-written `extern` declarations.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/Preprocessor/cnxt-prelude.c clang/test/Driver/cnxt-hello-world.c clang/test/Driver/cnxt-ownership-example.c clang/test/Driver/cnxt-interface-example.c`
  - `git diff --check`
- Next target: `M9-03`.

- Completed `M9-01`.
- Added `cnxt/specs/cnxt-ffi-boundary.md` to define where raw pointers are
  legal today, why `unsafe extern "C"` is required, and how ownership-handle
  raw escapes fit into that same FFI boundary.
- Updated `cnxt/README.md` to reference the new FFI-boundary baseline.
- Validation:
  - `build/bin/llvm-lit -sv clang/test/Parser/cnxt-ffi-raw-pointers.cpp clang/test/SemaCXX/cnxt-ownership-escapes.cpp clang/test/SemaCXX/cnxt-pointer-guidance-fixits.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp clang/test/CodeGenCXX/cnxt-ownership-runtime.cpp clang/test/CodeGenCXX/cnxt-weak-nullability.cpp`
  - `git diff --check`
- Next target: `M9-02`.

- Completed `M8-11`.
- Added `cnxt/examples/ownership/interface-counter.cn` as the end-to-end
  interface/class sample for unique ownership with no user-written
  `extern "C"` declarations.
- Added `clang/test/Driver/cnxt-interface-example.c` and updated
  `cnxt/README.md` so the documented flow now builds and runs the sample
  against the compiler-owned ownership runtime.
- Validation:
  - `build/bin/llvm-lit -sv clang/test/Driver/cnxt-interface-example.c clang/test/Driver/cnxt-ownership-example.c`
  - `build/bin/llvm-lit -sv clang/test/CodeGenCXX/cnxt-interface-ownership.cpp clang/test/CodeGenCXX/cnxt-interface-dispatch.cpp clang/test/SemaCXX/cnxt-interface-bindings.cpp`
  - `git diff --check`
- Next target: `M9-01`.

- Completed `M8-10`.
- Expanded interface/class regression coverage in:
  - `clang/test/Parser/cnxt-interface-decls.cpp`
  - `clang/test/SemaCXX/cnxt-interface-bindings.cpp`
  - `clang/test/CodeGenCXX/cnxt-interface-dispatch.cpp`
- Validation:
  - `build/bin/llvm-lit -sv clang/test/Parser/cnxt-interface-decls.cpp clang/test/Parser/cnxt-implements.cpp clang/test/SemaCXX/cnxt-interface-bindings.cpp clang/test/SemaCXX/cnxt-interface-conformance.cpp clang/test/SemaCXX/cnxt-interface-diagnostics.cpp clang/test/CodeGenCXX/cnxt-interface-dispatch.cpp clang/test/CodeGenCXX/cnxt-interface-ownership.cpp`
- Next target: `M8-11`.

- Completed `M8-09`.
- Preserved cNxt interface/class source spellings through interface carrier
  lowering in `SemaType.cpp` so clangd keeps written token locations for
  document symbols and references.
- Updated clangd behavior in:
  - `clang-tools-extra/clangd/FindSymbols.cpp`
  - `clang-tools-extra/clangd/SemanticHighlighting.cpp`
- Added/updated clangd regression coverage in:
  - `clang-tools-extra/clangd/unittests/FindSymbolsTests.cpp`
  - `clang-tools-extra/clangd/unittests/SemanticHighlightingTests.cpp`
  - `clang-tools-extra/clangd/unittests/XRefsTests.cpp`
- Validation:
  - `ninja -C build ClangdTests`
  - `build/tools/clang/tools/extra/clangd/unittests/ClangdTests --gtest_filter='DocumentSymbols.CNxtInterfaceAndClass:SemanticHighlighting.CNxtFileCoverage:LocateSymbol.CNxtInterfaceAndImplements:FindReferences.CNxtWithinAST:FindReferences.CNxtInterfaceWithinAST:FindReferences.CNxtClassWithinAST' --gtest_color=no`
  - `build/bin/llvm-lit -sv clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp clang/test/CodeGenCXX/cnxt-unique-cleanup.cpp clang/test/CodeGenCXX/cnxt-shared-refcount.cpp clang/test/CodeGenCXX/cnxt-weak-nullability.cpp clang/test/Preprocessor/cnxt-prelude.c`
  - `build/bin/llvm-lit -sv clang/test/SemaCXX/cnxt-interface-carrier.cpp clang/test/SemaCXX/cnxt-interface-conformance.cpp clang/test/SemaCXX/cnxt-interface-diagnostics.cpp`
- Follow-up note:
  - `CompletionTest.CNxtRankingAdjustments` remains a pre-existing unrelated
    clangd failure.
- Next target: `M8-10`.

- Completed `M8-08`.
- Added cNxt-specific diagnostics for non-interface `implements` entries and
  conflicting interface requirements in `SemaDeclCXX.cpp` /
  `DiagnosticSemaKinds.td`.
- Added regression coverage in:
  - `clang/test/SemaCXX/cnxt-interface-diagnostics.cpp`
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/SemaCXX/cnxt-interface-diagnostics.cpp clang/test/SemaCXX/cnxt-interface-conformance.cpp clang/test/SemaCXX/cnxt-interface-bindings.cpp clang/test/SemaCXX/cnxt-interface-ownership.cpp clang/test/Parser/cnxt-implements.cpp clang/test/Parser/cnxt-interface-decls.cpp clang/test/CodeGenCXX/cnxt-interface-dispatch.cpp clang/test/CodeGenCXX/cnxt-interface-ownership.cpp clang/test/Preprocessor/cnxt-prelude.c`
  - `git diff --check`
- Next target: `M8-09`.
- Completed `M8-07`.
- Extended the injected ownership prelude so `unique/shared/weak` preserve
  interface views and concrete destruction metadata across handle widening.
- Recovered borrowed interface views from ownership handles during member
  lookup so `owner.next()` and `observer.lock().next()` compile without
  `.get()` raw-pointer escapes.
- Added regression coverage in:
  - `clang/test/SemaCXX/cnxt-interface-ownership.cpp`
  - `clang/test/CodeGenCXX/cnxt-interface-ownership.cpp`
- Updated affected ownership ABI expectations in:
  - `clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp`
  - `clang/test/CodeGenCXX/cnxt-ownership-interop.cpp`
  - `clang/test/CodeGenCXX/cnxt-ownership-runtime.cpp`
  - `clang/test/CodeGenCXX/cnxt-share-widening.cpp`
  - `clang/test/CodeGenCXX/cnxt-weak-nullability.cpp`
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp clang/test/CodeGenCXX/cnxt-ownership-runtime.cpp clang/test/CodeGenCXX/cnxt-ownership-cleanup-paths.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp clang/test/CodeGenCXX/cnxt-shared-refcount.cpp clang/test/CodeGenCXX/cnxt-weak-nullability.cpp clang/test/CodeGenCXX/cnxt-interface-ownership.cpp clang/test/CodeGenCXX/cnxt-interface-dispatch.cpp clang/test/CodeGenCXX/cnxt-share-widening.cpp clang/test/SemaCXX/cnxt-interface-ownership.cpp clang/test/SemaCXX/cnxt-interface-bindings.cpp clang/test/SemaCXX/cnxt-interface-conformance.cpp clang/test/SemaCXX/cnxt-ownership-runtime.cpp clang/test/Parser/cnxt-ownership-runtime-surface.cpp clang/test/Preprocessor/cnxt-prelude.c`
  - `git diff --check`
- Next target: `M8-08`.
- Completed `M8-06`.
- Recovered interface pointers from `__cnxt_iface_borrowed<T>` during member
  lookup so borrowed interface calls like `view.next()` lower through normal
  virtual-call codegen.
- Made cNxt `implements` interface bases public by default and tightened the
  carrier converting constructor so it only accepts actual implementing types.
- Added regression coverage in:
  - `clang/test/CodeGenCXX/cnxt-interface-dispatch.cpp`
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/CodeGenCXX/cnxt-interface-dispatch.cpp clang/test/SemaCXX/cnxt-interface-bindings.cpp clang/test/SemaCXX/cnxt-interface-conformance.cpp clang/test/SemaCXX/cnxt-interface-carrier.cpp clang/test/Preprocessor/cnxt-prelude.c clang/test/Parser/cnxt-implements.cpp clang/test/Parser/cnxt-interface-decls.cpp`
  - `git diff --check`
- Next target: `M8-07`.
- Completed `M8-05b`.
- Rewrote cNxt interface-valued declarations in `SemaType.cpp` onto
  `__cnxt_iface_borrowed<Interface>` for locals, globals, parameters, and
  returns while excluding type-name-only contexts like `implements`.
- Extended the injected carrier in `InitPreprocessor.cpp` with a concrete-type
  constructor so implementing classes bind directly to interface carriers.
- Added regression coverage in:
  - `clang/test/SemaCXX/cnxt-interface-bindings.cpp`
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/SemaCXX/cnxt-interface-bindings.cpp clang/test/SemaCXX/cnxt-interface-carrier.cpp clang/test/SemaCXX/cnxt-interface-conformance.cpp clang/test/Preprocessor/cnxt-prelude.c clang/test/Parser/cnxt-implements.cpp clang/test/Parser/cnxt-interface-decls.cpp clang/test/Parser/cnxt-construction.cpp clang/test/SemaCXX/cnxt-construction.cpp`
  - `git diff --check`
- Next target: `M8-06`.
- Completed `M8-05a`.
- Added compiler-owned borrowed interface carrier templates
  `__cnxt_iface_witness<T>` / `__cnxt_iface_borrowed<T>` to the injected cNxt
  prelude and allowed the hidden carrier template through the cNxt template
  gate.
- Added regression coverage in:
  - `clang/test/Preprocessor/cnxt-prelude.c`
  - `clang/test/SemaCXX/cnxt-interface-carrier.cpp`
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/Preprocessor/cnxt-prelude.c clang/test/SemaCXX/cnxt-interface-carrier.cpp clang/test/SemaCXX/cnxt-interface-conformance.cpp clang/test/Parser/cnxt-implements.cpp clang/test/Parser/cnxt-interface-decls.cpp clang/test/Parser/cnxt-construction.cpp clang/test/SemaCXX/cnxt-construction.cpp`
  - `git diff --check`
- Next target: `M8-05b`.
- Completed `M8-04`.
- Added cNxt-specific interface conformance diagnostics for missing methods,
  incompatible signatures, and non-public implementations in
  `SemaDeclCXX.cpp` / `DiagnosticSemaKinds.td`.
- Added `clang/test/SemaCXX/cnxt-interface-conformance.cpp` and updated
  `clang/test/Parser/cnxt-implements.cpp` so positive parser coverage stays
  valid under the new visibility rule.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/SemaCXX/cnxt-interface-conformance.cpp clang/test/Parser/cnxt-implements.cpp clang/test/Parser/cnxt-interface-decls.cpp clang/test/Parser/cnxt-restrictions.cpp clang/test/Parser/cnxt-recovery.cpp`
  - `git diff --check`
- Direction check:
  - split the original `M8-05` into `M8-05a` and `M8-05b` because the codebase
    still models cNxt interfaces as abstract C++ bases, and the next safe
    steps are to land carrier representation and binding enablement separately.
- Next target: `M8-05a`.
- Completed `M6-01`.
- Added ownership runtime ABI baseline spec at
  `cnxt/specs/cnxt-ownership-runtime.md`.
- Linked new spec from `cnxt/README.md`.
- Updated `ROADMAP.md` status/priority and added M6-01 completion-log entry.
- Completed `M6-02`.
- Replaced cNxt prelude std-alias flow with compiler-owned `unique/shared/weak`
  handle declarations in `InitPreprocessor.cpp`.
- Updated ownership conversion classification and cNxt prelude/codegen/parser
  regression tests for new handle names.
- Validation:
  `build/bin/llvm-lit -sv clang/test/Preprocessor/cnxt-prelude.c clang/test/Parser/cnxt-ownership.cpp clang/test/Parser/cnxt-unique-lowering.cpp clang/test/Parser/cnxt-shared-lowering.cpp clang/test/Parser/cnxt-weak-lowering.cpp clang/test/Parser/cnxt-unique-move-only.cpp clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp`
- Completed `M6-03`.
- Added ownership runtime skeleton:
  - `cnxt/runtime/ownership/include/cnxt/runtime/ownership.h`
  - `cnxt/runtime/ownership/src/ownership_runtime.cpp`
  - `cnxt/runtime/ownership/CMakeLists.txt`
  - `cnxt/runtime/ownership/README.md`
- Validation:
  - `cmake -S cnxt/runtime/ownership -B /tmp/cnxt-ownership-rt-build -DCMAKE_BUILD_TYPE=Release`
  - `cmake --build /tmp/cnxt-ownership-rt-build -j4`
  - `nm -D /tmp/cnxt-ownership-rt-build/libcnxt_ownership_rt.so.1 | rg "__cnxt_rt_own_v1_"`
- Next target: `M6-04`.
- Completed `M6-04`.
- Updated cNxt injected prelude lowering so ownership operations call runtime ABI
  symbols (`__cnxt_rt_own_v1_*`) instead of pointer-only shims.
- Updated CodeGen checks to assert runtime-call lowering for
  `weak<T>.lock()` / `weak<T>.expired()`.
- Validation:
  `build/bin/llvm-lit -sv clang/test/Preprocessor/cnxt-prelude.c clang/test/Parser/cnxt-ownership.cpp clang/test/Parser/cnxt-unique-lowering.cpp clang/test/Parser/cnxt-shared-lowering.cpp clang/test/Parser/cnxt-weak-lowering.cpp clang/test/Parser/cnxt-unique-move-only.cpp clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp`
- Next target: `M6-05`.
- Completed `M6-05`.
- Added automatic `unique<T>` scope-exit cleanup by injecting a `unique`
  destructor that routes through `reset()` and runtime-backed `unique_drop`.
- Added `clang/test/CodeGenCXX/cnxt-unique-cleanup.cpp` to prove cleanup on
  fallthrough, `return`, `break`, and `continue`.
- Validation:
  `build/bin/llvm-lit -sv clang/test/CodeGenCXX/cnxt-unique-cleanup.cpp clang/test/Preprocessor/cnxt-prelude.c clang/test/Parser/cnxt-ownership.cpp clang/test/Parser/cnxt-unique-lowering.cpp clang/test/Parser/cnxt-shared-lowering.cpp clang/test/Parser/cnxt-weak-lowering.cpp clang/test/Parser/cnxt-unique-move-only.cpp clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp`
- Next target: `M6-06`.
- Completed `M6-06`.
- Added `clang/test/CodeGenCXX/cnxt-shared-refcount.cpp` to verify runtime
  retain/release lowering for shared copy, move, assignment, and destruction.
- Validation:
  `build/bin/llvm-lit -sv clang/test/CodeGenCXX/cnxt-shared-refcount.cpp clang/test/CodeGenCXX/cnxt-unique-cleanup.cpp clang/test/Preprocessor/cnxt-prelude.c clang/test/Parser/cnxt-ownership.cpp clang/test/Parser/cnxt-unique-lowering.cpp clang/test/Parser/cnxt-shared-lowering.cpp clang/test/Parser/cnxt-weak-lowering.cpp clang/test/Parser/cnxt-unique-move-only.cpp clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp`
- Next target: `M6-07` or `M6-09` pending direction check.
- Completed `M6-09`.
- Tightened `clang/test/Preprocessor/cnxt-prelude.c` to assert no `<memory>` or
  `std::*ptr` spellings appear in the injected cNxt prelude.
- Added a `-nostdinc++` syntax-only regression so `unique/shared/weak` remain
  available without host C++ standard library headers.
- Validation:
  `build/bin/llvm-lit -sv clang/test/Preprocessor/cnxt-prelude.c clang/test/CodeGenCXX/cnxt-shared-refcount.cpp clang/test/CodeGenCXX/cnxt-unique-cleanup.cpp clang/test/Parser/cnxt-ownership.cpp clang/test/Parser/cnxt-unique-lowering.cpp clang/test/Parser/cnxt-shared-lowering.cpp clang/test/Parser/cnxt-weak-lowering.cpp clang/test/Parser/cnxt-unique-move-only.cpp clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp`
- Next target: `M6-07`.
- Completed `M6-07`.
- Added `clang/test/CodeGenCXX/cnxt-weak-nullability.cpp` to verify default
  weak handles lower to null-control semantics and route `lock()` / `expired()`
  through the runtime ABI with explicit nullability checks.
- Validation:
  `build/bin/llvm-lit -sv clang/test/CodeGenCXX/cnxt-weak-nullability.cpp clang/test/Preprocessor/cnxt-prelude.c clang/test/CodeGenCXX/cnxt-shared-refcount.cpp clang/test/CodeGenCXX/cnxt-unique-cleanup.cpp clang/test/Parser/cnxt-ownership.cpp clang/test/Parser/cnxt-unique-lowering.cpp clang/test/Parser/cnxt-shared-lowering.cpp clang/test/Parser/cnxt-weak-lowering.cpp clang/test/Parser/cnxt-unique-move-only.cpp clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp`
- Next target: `M6-08`.
- Completed `M6-08`.
- Added driver-side cNxt ownership-runtime validation with
  `-fcnxt-ownership-runtime=<path>`.
- Added cNxt-specific diagnostics for missing runtime configuration, load
  failures, missing ABI symbol, and unsupported ABI version, and appended the
  validated runtime path to cNxt link inputs.
- Added Linux driver coverage in `clang/test/Driver/cnxt-ownership-runtime.c`
  plus tiny shared-library fixtures under `clang/test/Driver/Inputs/`.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/Driver/cnxt-driver.c clang/test/Driver/cnxt-ownership-runtime.c`
- Next target: `M6-10`.
- Completed `M6-10`.
- Added parser, `SemaCXX`, and `CodeGenCXX` ownership-runtime regression tests:
  - `clang/test/Parser/cnxt-ownership-runtime-surface.cpp`
  - `clang/test/SemaCXX/cnxt-ownership-runtime.cpp`
  - `clang/test/CodeGenCXX/cnxt-ownership-runtime.cpp`
- Validation:
  `build/bin/llvm-lit -sv clang/test/Parser/cnxt-ownership.cpp clang/test/Parser/cnxt-ownership-baseline.cpp clang/test/Parser/cnxt-ownership-conversions.cpp clang/test/Parser/cnxt-unique-lowering.cpp clang/test/Parser/cnxt-shared-lowering.cpp clang/test/Parser/cnxt-weak-lowering.cpp clang/test/Parser/cnxt-unique-move-only.cpp clang/test/Parser/cnxt-shared-copy-rules.cpp clang/test/Parser/cnxt-weak-lock-required.cpp clang/test/Parser/cnxt-ownership-runtime-surface.cpp clang/test/SemaCXX/cnxt-ownership-baseline.cpp clang/test/SemaCXX/cnxt-ownership-runtime.cpp clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp clang/test/CodeGenCXX/cnxt-unique-cleanup.cpp clang/test/CodeGenCXX/cnxt-shared-refcount.cpp clang/test/CodeGenCXX/cnxt-weak-nullability.cpp clang/test/CodeGenCXX/cnxt-ownership-runtime.cpp`
- Next target: `M6-11`.
- Completed `M6-11`.
- Added standalone ownership runtime smoke coverage under
  `cnxt/runtime/ownership/tests/ownership_runtime_smoke.cpp` for clean
  lifecycle, leak, and double-free paths.
- Extended `cnxt/runtime/ownership/CMakeLists.txt` with `BUILD_TESTING`,
  sanitizer instrumentation support, and CTest wiring for clean and expected
  sanitizer-failure paths.
- Added `cnxt/runtime/ownership/cmake/expect_sanitizer_failure.cmake` so
  leak/double-free tests require the expected ASan/LSan diagnostics.
- Added `.github/workflows/cnxt-ownership-runtime-sanitizers.yml` to build and
  run the standalone ownership runtime sanitizer suite in CI.
- Validation:
  - `cmake -S cnxt/runtime/ownership -B /tmp/cnxt-ownership-sanitizers -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_CXX_COMPILER=/usr/bin/c++ -DBUILD_TESTING=ON -DCNXT_OWNERSHIP_RT_ENABLE_SANITIZERS=ON`
  - `cmake --build /tmp/cnxt-ownership-sanitizers --parallel`
  - `ctest --test-dir /tmp/cnxt-ownership-sanitizers --output-on-failure`
  - `cmake -S cnxt/runtime/ownership -B /tmp/cnxt-ownership-default -G Ninja -DCMAKE_CXX_COMPILER=/usr/bin/c++ -DBUILD_TESTING=ON`
  - `cmake --build /tmp/cnxt-ownership-default --parallel`
  - `ctest --test-dir /tmp/cnxt-ownership-default --output-on-failure`
- Next target: `M6-12`.
- Completed `M6-12`.
- Exposed `__cnxt_rt_own_v1_alloc` in the injected cNxt prelude and added a
  compiler-owned `make_unique(value)` helper so the example path needs no
  user-written `extern "C"` ownership declarations.
- Added `cnxt/examples/ownership/unique-heap.cn` plus README build/run commands
  showing the current end-to-end ownership flow on this branch.
- Added `clang/test/Driver/cnxt-ownership-example.c` to build the standalone
  ownership runtime, compile the sample in cNxt mode, and execute it on native
  Linux.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/Driver/cnxt-ownership-example.c clang/test/Preprocessor/cnxt-prelude.c`
  - `build/bin/clang++ -shared -fPIC -std=c++17 -Icnxt/runtime/ownership/include cnxt/runtime/ownership/src/ownership_runtime.cpp -o /tmp/libcnxt_ownership_rt.so`
  - `build/bin/clang++ -x cnxt -std=cnxt1 cnxt/examples/ownership/unique-heap.cn -fcnxt-ownership-runtime=/tmp/libcnxt_ownership_rt.so -o /tmp/cnxt-unique-heap`
  - `env LD_LIBRARY_PATH=/tmp /tmp/cnxt-unique-heap`
- Next target: `M7-01`.
- Completed `M7-01`.
- Added `cnxt/specs/cnxt-construction-api.md` as the source of truth for the
  intended `make<T>(...) -> unique<T>` construction surface.
- Linked the new construction spec from `cnxt/README.md`.
- Recorded that the Milestone 6 `make_unique(value)` helper is transitional and
  that Milestone 7 implementation work should converge on `make<T>(...)`.
- Validation:
  - `git diff --check`
  - `rg -n "cnxt-construction-api.md|M7-01|M7-02" ROADMAP.md SESSION_LOG.md cnxt/README.md`
- Next target: `M7-02`.
- Completed `M7-02`.
- Extended the cNxt template-id allowlist so `make<T>(...)` parses while
  unrelated template argument lists remain rejected.
- Added a prelude declaration for `make<T>(Args...)` and parser/`SemaCXX`
  coverage in:
  - `clang/test/Parser/cnxt-construction.cpp`
  - `clang/test/SemaCXX/cnxt-construction.cpp`
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/Parser/cnxt-construction.cpp clang/test/SemaCXX/cnxt-construction.cpp clang/test/Parser/cnxt-ownership.cpp clang/test/Preprocessor/cnxt-prelude.c`
- Next target: `M7-03`.
- Completed `M7-03`.
- Added `err_cnxt_invalid_construction_target` and cNxt `make<T>(...)` payload
  screening in `clang/lib/Sema/SemaExpr.cpp` for explicit-template-argument and
  resolved-call paths.
- Updated the compiler-owned `unique<T>::reset` prelude in
  `clang/lib/Frontend/InitPreprocessor.cpp` so incomplete payloads do not
  cascade `alignof(T)` diagnostics after the intended construction error.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/Parser/cnxt-construction.cpp clang/test/SemaCXX/cnxt-construction.cpp clang/test/Parser/cnxt-ownership.cpp clang/test/Preprocessor/cnxt-prelude.c`
  - `build/bin/llvm-lit -sv clang/test/CodeGenCXX/cnxt-unique-cleanup.cpp clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp`
- Next target: `M7-04`.
- Completed `M7-04`.
- Replaced the injected prelude's declaration-only `make<T>(...)` with a real
  runtime-backed definition that allocates via `__cnxt_rt_own_v1_alloc`,
  performs in-place construction, and returns `unique<T>`.
- Added a system-header-only placement `new` helper plus an
  `__is_complete_type(T)` guard so valid construction lowers cleanly while
  incomplete payloads do not emit stray `sizeof(T)` diagnostics.
- Updated `cnxt/examples/ownership/unique-heap.cn` and `cnxt/README.md` to use
  `make<T>(...)`, and added `clang/test/CodeGenCXX/cnxt-construction.cpp`.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/CodeGenCXX/cnxt-construction.cpp clang/test/SemaCXX/cnxt-construction.cpp clang/test/Parser/cnxt-construction.cpp clang/test/Parser/cnxt-ownership.cpp clang/test/Parser/cnxt-restrictions.cpp clang/test/Preprocessor/cnxt-prelude.c clang/test/Driver/cnxt-ownership-example.c clang/test/CodeGenCXX/cnxt-unique-cleanup.cpp clang/test/CodeGenCXX/cnxt-ownership-baseline.cpp`
- Next target: `M7-05`.
- Completed `M7-05`.
- Added compiler-owned `share(unique<T> &&)` widening in the injected prelude,
  backed by `__cnxt_rt_own_v1_shared_from_unique`, so safe cNxt code can move
  from `unique<T>` to `shared<T>` without raw-pointer intermediates.
- Added payload metadata helpers so unique cleanup and shared widening preserve
  destructor, size, and alignment metadata for non-trivial payloads.
- Updated `cnxt/specs/cnxt-construction-api.md` to name
  `share(unique<T>) -> shared<T>` as the explicit post-construction widening
  step.
- Added focused coverage in:
  - `clang/test/Preprocessor/cnxt-prelude.c`
  - `clang/test/Parser/cnxt-ownership-runtime-surface.cpp`
  - `clang/test/SemaCXX/cnxt-ownership-runtime.cpp`
  - `clang/test/CodeGenCXX/cnxt-share-widening.cpp`
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/Preprocessor/cnxt-prelude.c clang/test/Parser/cnxt-ownership-runtime-surface.cpp clang/test/SemaCXX/cnxt-ownership-runtime.cpp clang/test/CodeGenCXX/cnxt-share-widening.cpp clang/test/CodeGenCXX/cnxt-ownership-runtime.cpp clang/test/CodeGenCXX/cnxt-shared-refcount.cpp clang/test/CodeGenCXX/cnxt-construction.cpp clang/test/SemaCXX/cnxt-construction.cpp clang/test/Parser/cnxt-construction.cpp clang/test/Driver/cnxt-ownership-example.c`
- Next target: `M7-06`.
- Completed `M7-06`.
- Added `err_cnxt_ownership_raw_escape` and an early `BuildCallExpr` check so
  bound member calls like `unique<T>::get()`, `unique<T>::release()`, and
  `shared<T>::get()` are rejected in safe cNxt code.
- Kept the temporary allowance limited to system-header code and `extern "C"`
  bodies so the injected prelude and current FFI seams continue to compile
  while M7-07 replaces the linkage carveout with an explicit unsafe model.
- Updated safe-code parser/`SemaCXX` coverage to stop relying on raw escapes,
  added `clang/test/SemaCXX/cnxt-ownership-escapes.cpp`, and rewrote
  `cnxt/examples/ownership/unique-heap.cn` to stay within safe ownership
  semantics.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/SemaCXX/cnxt-ownership-escapes.cpp clang/test/Parser/cnxt-unique-lowering.cpp clang/test/Parser/cnxt-shared-lowering.cpp clang/test/Parser/cnxt-weak-lock-required.cpp clang/test/Parser/cnxt-ownership-runtime-surface.cpp clang/test/SemaCXX/cnxt-ownership-runtime.cpp clang/test/CodeGenCXX/cnxt-ownership-runtime.cpp clang/test/CodeGenCXX/cnxt-weak-nullability.cpp clang/test/CodeGenCXX/cnxt-share-widening.cpp clang/test/Preprocessor/cnxt-prelude.c clang/test/Parser/cnxt-construction.cpp clang/test/SemaCXX/cnxt-construction.cpp clang/test/Driver/cnxt-ownership-example.c`
  - `git diff --check`
- Next target: `M7-07`.
- Completed `M7-07`.
- Added a contextual `unsafe` marker before `extern` in cNxt declaration
  parsing and carried it through `DeclSpec` so `unsafe extern "C"` can mark
  explicit FFI boundaries.
- Replaced the old plain-`extern "C"` carveout with an explicit
  `cnxt_unsafe_extern` annotation on `FunctionDecl`, and switched both
  raw-pointer signature checks and ownership-handle raw-escape checks to use
  that explicit boundary.
- Updated coverage so plain `extern "C"` now remains rejected for raw-pointer
  signatures and `.get()` / `.release()` escapes, while targeted parser,
  `SemaCXX`, codegen, and interop tests use `unsafe extern "C"` where they
  intentionally exercise FFI behavior.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/Parser/cnxt-ffi-raw-pointers.cpp clang/test/SemaCXX/cnxt-ownership-escapes.cpp clang/test/Parser/cnxt-restrictions.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp clang/test/Parser/cnxt-unique-lowering.cpp clang/test/Parser/cnxt-shared-lowering.cpp clang/test/Parser/cnxt-weak-lock-required.cpp clang/test/Parser/cnxt-ownership-runtime-surface.cpp clang/test/SemaCXX/cnxt-ownership-runtime.cpp clang/test/CodeGenCXX/cnxt-ownership-runtime.cpp clang/test/CodeGenCXX/cnxt-weak-nullability.cpp clang/test/CodeGenCXX/cnxt-share-widening.cpp clang/test/Preprocessor/cnxt-prelude.c clang/test/Parser/cnxt-construction.cpp clang/test/SemaCXX/cnxt-construction.cpp clang/test/Driver/cnxt-ownership-example.c`
  - `git diff --check`
- Next target: `M7-08`.
- Completed `M7-08`.
- Added ownership-guidance notes for raw-pointer declaration/signature/escape
  diagnostics and taught plain `extern "C"` raw-pointer errors to offer an
  `unsafe extern "C"` fix-it at the actual `extern` token.
- Recorded cNxt extern-linkage source locations on `FunctionDecl` so later
  ownership-handle raw-escape diagnostics can reuse the same fix-it inside
  function bodies without inserting `unsafe` in the wrong spot.
- Added `clang/test/SemaCXX/cnxt-pointer-guidance-fixits.cpp` and updated the
  existing raw-pointer/escape `-verify` tests to ignore the new intentional
  notes while the dedicated fix-it test locks in the exact guidance surface.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/SemaCXX/cnxt-pointer-guidance-fixits.cpp clang/test/Parser/cnxt-ffi-raw-pointers.cpp clang/test/SemaCXX/cnxt-ownership-escapes.cpp clang/test/Parser/cnxt-restrictions.cpp clang/test/CodeGenCXX/cnxt-ownership-interop.cpp clang/test/Parser/cnxt-unique-lowering.cpp clang/test/Parser/cnxt-shared-lowering.cpp clang/test/Parser/cnxt-weak-lock-required.cpp clang/test/Parser/cnxt-ownership-runtime-surface.cpp clang/test/SemaCXX/cnxt-ownership-runtime.cpp clang/test/CodeGenCXX/cnxt-ownership-runtime.cpp clang/test/CodeGenCXX/cnxt-weak-nullability.cpp clang/test/CodeGenCXX/cnxt-share-widening.cpp clang/test/Preprocessor/cnxt-prelude.c clang/test/Parser/cnxt-construction.cpp clang/test/SemaCXX/cnxt-construction.cpp clang/test/Driver/cnxt-ownership-example.c`
  - `git diff --check`
- Next target: `M7-09`.
- Completed `M7-09`.
- Added `clang/test/CodeGenCXX/cnxt-ownership-cleanup-paths.cpp` to prove that
  `make<T>(...)` results clean up through a shared early-return cleanup block
  and that branch-local `share(make<T>(...))` values release both the temporary
  `unique<T>` and the widened `shared<T>` before control rejoins.
- Kept the checks at the IR control-flow level so the test pins the cleanup
  block shape instead of only spotting destructor calls somewhere in the
  function body.
- Validation:
  - `build/bin/llvm-lit -sv clang/test/CodeGenCXX/cnxt-ownership-cleanup-paths.cpp clang/test/CodeGenCXX/cnxt-unique-cleanup.cpp clang/test/CodeGenCXX/cnxt-construction.cpp clang/test/CodeGenCXX/cnxt-share-widening.cpp clang/test/CodeGenCXX/cnxt-shared-refcount.cpp`
  - `git diff --check`
- Next target: `M7-10`.
- Completed `M7-10`.
- Added `cnxt/examples/ownership/class-method.cn`, which constructs a class
  instance, calls a method with ordinary class syntax, then creates an owned
  `unique<Counter>` through `make<Counter>(...)` and lets scope exit clean it
  up with no raw-pointer syntax or glue file.
- Updated `cnxt/README.md` and `clang/test/Driver/cnxt-ownership-example.c` so
  the documented and tested end-to-end flow now builds and runs that no-glue
  class example against the ownership runtime.
- Validation:
  - `build/bin/llvm-lit -sv clang/test/Driver/cnxt-ownership-example.c`
  - `git diff --check`
- Next target: `M8-01`.
- Completed `M8-01`.
- Added `cnxt/specs/cnxt-interface-class.md` as the Milestone 8 source of
  truth for `interface` declarations, `class ... implements ...` syntax,
  conformance rules, witness-table dispatch, and the explicit deferral of
  ownership-over-interface behavior to `M8-07`.
- Validation:
  - `git diff --check`
- Next target: `M8-02`.
- Completed `M8-02`.
- Added a cNxt-only contextual `interface` declaration spelling in
  `clang/lib/Parse/ParseDecl.cpp` and routed it through the existing
  `__interface` parser path without making ordinary identifier uses of
  `interface` illegal in expressions.
- Added `clang/test/Parser/cnxt-interface-decls.cpp` to cover forward
  declarations, definitions, contextual-keyword disambiguation, and base-clause
  rejection on interface declarations.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/Parser/cnxt-interface-decls.cpp clang/test/Parser/cnxt-restrictions.cpp clang/test/Parser/cnxt-recovery.cpp`
  - `git diff --check`
- Next target: `M8-03`.
- Completed `M8-03`.
- Added parser support for `class ... implements ...` in
  `clang/lib/Parse/ParseDeclCXX.cpp`, parsing the interface list through the
  existing base-specifier machinery while still rejecting raw `:` inheritance in
  cNxt.
- Added `clang/test/Parser/cnxt-implements.cpp` covering native `implements`
  clauses, multiple interfaces, and contextual use of `implements` as an
  ordinary identifier outside class headers.
- Validation:
  - `ninja -C build clang`
  - `build/bin/llvm-lit -sv clang/test/Parser/cnxt-implements.cpp clang/test/Parser/cnxt-interface-decls.cpp clang/test/Parser/cnxt-restrictions.cpp clang/test/Parser/cnxt-recovery.cpp`
  - `git diff --check`
- Next target: `M8-04`.
- Completed `M10-02`.
- Added `clang-cnxt-fuzzer`, a syntax-only cNxt fuzzer entrypoint backed by a
  new `HandleCXXSyntaxOnly` helper so raw-text fuzzing can run in
  `-x cnxt -std=cnxt1` mode without changing the existing C++ fuzzer behavior.
- Added cNxt corpus seeds under `clang/tools/clang-fuzzer/corpus_examples/cnxt/`
  covering ownership, construction, interface bindings, and `unsafe extern`
  boundaries, plus `clang/test/Misc/cnxt-fuzzer-corpus.test` to compile those
  seeds with `-verify`.
- Updated `clang/tools/clang-fuzzer/README.txt` with build/run instructions for
  the new cNxt fuzz target and corpus path.
- Validation:
  - `ninja -C build clang-fuzzer clang-cnxt-fuzzer`
  - `build/bin/llvm-lit -sv clang/test/Misc/cnxt-fuzzer-corpus.test`
  - `build/bin/clang-cnxt-fuzzer clang/tools/clang-fuzzer/corpus_examples/cnxt/ownership-lifetimes.cn`
  - `git diff --check`
- Next target: `M10-03`.

- Completed `M10-03`.
- Added `cnxt/runtime/ownership/benchmarks/ownership_dispatch_bench.cpp`, a
  standalone microbenchmark binary that reports ns/op for runtime `unique`
  drop, `shared` copy/release, `weak_lock` hit/miss, and borrowed witness
  dispatch alongside `std::*` and direct-call baselines.
- Updated `cnxt/runtime/ownership/CMakeLists.txt` to build
  `cnxt_ownership_rt_bench` and link the existing smoke target against
  `Threads::Threads`, which was required to keep the runtime test build
  portable on a plain `c++` toolchain.
- Updated `cnxt/runtime/ownership/README.md` with benchmark build/run commands.
- Local baseline snapshot from
  `cnxt_ownership_rt_bench --iterations 200000 --json`:
  `runtime_unique_drop` `26.32 ns/op` (`1.27x` vs `std_unique_drop`),
  `runtime_shared_copy_release` `16.04 ns/op` (`4.18x` vs `std_shared_copy`),
  `runtime_weak_lock_hit` `18.87 ns/op` (`1.73x` vs `std_weak_lock_hit`),
  `runtime_weak_lock_miss` `5.01 ns/op` (`1.55x` vs `std_weak_lock_miss`),
  `witness_dispatch` `2.06 ns/op` (`1.17x` vs `direct_dispatch`).
- Validation:
  - `cmake -S cnxt/runtime/ownership -B /tmp/cnxt-ownership-bench -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=c++ -DBUILD_TESTING=ON`
  - `cmake --build /tmp/cnxt-ownership-bench --parallel`
  - `/tmp/cnxt-ownership-bench/cnxt_ownership_rt_bench --iterations 200000 --json`
  - `ctest --test-dir /tmp/cnxt-ownership-bench --output-on-failure`
  - `git diff --check`
- Next target: `M10-04`.

- Completed `M10-04`.
- Added `.github/workflows/cnxt-compiler-matrix.yml`, a GitHub Actions matrix
  workflow for `ubuntu-24.04` and `macos-14` that:
  configures/builds/tests the standalone ownership runtime, captures
  `cnxt_ownership_rt_bench --json`, builds a minimal `clang` test toolchain,
  and runs a curated 22-test cNxt `llvm-lit` slice covering M6-M9 features.
- Kept the existing Linux-only sanitizer and IDE workflows intact; the new
  workflow is the cross-platform representative coverage layer rather than a
  replacement for those focused jobs.
- Validation:
  - `cmake -S cnxt/runtime/ownership -B /tmp/cnxt-ownership-bench -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=c++ -DBUILD_TESTING=ON`
  - `cmake --build /tmp/cnxt-ownership-bench --parallel`
  - `ctest --test-dir /tmp/cnxt-ownership-bench --output-on-failure`
  - `build/bin/llvm-lit -sv clang/test/Preprocessor/cnxt-prelude.c clang/test/Parser/cnxt-ownership-runtime-surface.cpp clang/test/CodeGenCXX/cnxt-ownership-runtime.cpp clang/test/CodeGenCXX/cnxt-unique-cleanup.cpp clang/test/CodeGenCXX/cnxt-shared-refcount.cpp clang/test/CodeGenCXX/cnxt-weak-nullability.cpp clang/test/Parser/cnxt-construction.cpp clang/test/SemaCXX/cnxt-construction.cpp clang/test/CodeGenCXX/cnxt-construction.cpp clang/test/CodeGenCXX/cnxt-share-widening.cpp clang/test/SemaCXX/cnxt-ownership-escapes.cpp clang/test/SemaCXX/cnxt-pointer-guidance-fixits.cpp clang/test/Parser/cnxt-interface-decls.cpp clang/test/Parser/cnxt-implements.cpp clang/test/SemaCXX/cnxt-interface-bindings.cpp clang/test/SemaCXX/cnxt-interface-ownership.cpp clang/test/CodeGenCXX/cnxt-interface-dispatch.cpp clang/test/CodeGenCXX/cnxt-interface-ownership.cpp clang/test/Parser/cnxt-ffi-raw-pointers.cpp clang/test/SemaCXX/cnxt-c-abi-pointer-guidance.cpp clang/test/CodeGenCXX/cnxt-c-abi-thunks.cpp clang/test/CodeGenCXX/cnxt-c-abi-ownership-marshalling.cpp`
  - `git diff --check`
- Follow-up note:
  the macOS leg was validated structurally through the workflow definition but
  still needs its first hosted GitHub Actions run for end-to-end confirmation.
- Next target: `M10-05`.

- Completed `M10-05`.
- Added `cnxt/docs/quickstart.md`, a repo-local quickstart that walks through
  the no-glue starter app, the direct ownership/interface examples, and the
  exact checks showing those shipped examples contain no manual `extern "C"` or
  `unsafe extern` glue.
- Linked that quickstart from `cnxt/README.md` so the no-glue path is visible
  from the main cNxt landing page.
- Validation:
  - `python3 cnxt/tools/tests/test_e2e_starter_template.py`
  - `build/bin/llvm-lit -sv clang/test/Driver/cnxt-ownership-example.c clang/test/Driver/cnxt-interface-example.c`
  - `rg -n 'extern "C"|unsafe extern' cnxt/examples/starter/hello-app cnxt/examples/ownership/class-method.cn cnxt/examples/ownership/interface-counter.cn`
  - `git diff --check`
- Follow-up note:
  the `rg` command is expected to return no matches, and that is the intended
  success condition recorded by the quickstart.
- Next target: `M10-06`.

- Completed `M10-06`.
- Added `cnxt/docs/acceptance-checklist.md`, which names the exact workflows,
  artifacts, docs, and starter-template conditions that must be true before
  Milestone 10 is considered complete.
- Updated `cnxt/tools/tests/test_e2e_starter_template.py` to accept
  `CNXT_TEST_CLANGXX`, then wired `.github/workflows/cnxt-compiler-matrix.yml`
  to run that starter-template e2e test on the Linux matrix leg after building
  `clang`, making the no-glue sample app an explicit CI gate.
- Linked the acceptance checklist from `cnxt/README.md`.
- Validation:
  - `CNXT_TEST_CLANGXX=$(pwd)/build/bin/clang++ python3 cnxt/tools/tests/test_e2e_starter_template.py`
  - `git diff --check`
- Follow-up note:
  the macOS matrix leg still contributes cross-platform runtime/compiler
  coverage, but the explicit package-tool starter gate is Linux-only today.
- Next target: none; Milestone 10 backlog is complete.
