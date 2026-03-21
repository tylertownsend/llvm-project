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
