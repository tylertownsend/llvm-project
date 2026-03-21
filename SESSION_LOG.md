# SESSION_LOG

## 2026-03-21

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
