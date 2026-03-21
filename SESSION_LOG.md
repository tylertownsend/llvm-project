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
