# cNxt M3-00 Feasibility Spike

## Goal

Determine whether cNxt can use `unique/shared/weak` as language-level handles
while lowering to C++ memory machinery without requiring user-authored
`#include <memory>` in source files.

## Experiment Matrix

### Case 1: C++ control (expected to work)

Command:

```bash
printf 'int main(){ std::unique_ptr<int> p; return 0; }\n' \
  | build/bin/clang -x c++ -std=c++20 -include memory -fsyntax-only -
```

Result:

- Passes (exit code 0).

Interpretation:

- Toolchain and standard library wiring are healthy for std-backed handles.

### Case 2: cNxt without prelude/include

Command:

```bash
printf 'int main(){ std::unique_ptr<int> p; return 0; }\n' \
  | build/bin/clang -x cnxt -std=cnxt1 -fsyntax-only -
```

Result:

- Fails (undeclared `std` and follow-on parse/type errors).

Interpretation:

- cNxt currently has no injected ownership prelude.

### Case 3: cNxt with forced `-include memory`

Command:

```bash
printf 'int main(){ std::unique_ptr<int> p; return 0; }\n' \
  | build/bin/clang -x cnxt -std=cnxt1 -include memory -fsyntax-only -
```

Result:

- Fails immediately with cNxt include policy diagnostic:
  `cNxt does not support textual include directives; use module imports`.

Interpretation:

- Current milestone-2 include restrictions apply to compiler-forced textual
  includes as well, so this path is blocked.

## Feasibility Conclusion

Std-backed ownership handles are feasible in principle (Case 1), but cNxt is
currently blocked by frontend policy and language-surface constraints:

1. No compiler-owned prelude currently introduces ownership handles.
2. Textual include policy blocks `-include memory` in cNxt mode.
3. cNxt restriction checks are currently global; future std-backed lowering
   likely needs a compiler-owned boundary (module or controlled prelude) where
   host-C++ mechanisms remain available.

## Fallback Constraints (if direct std-backing remains blocked)

1. Implement a cNxt-owned ownership runtime with ABI-compatible wrappers that
   do not expose standard library headers to user source.
2. Introduce an internal-only lowering layer that maps cNxt handles to backend
   primitives without requiring direct `std::` names in parsed cNxt code.

## Unblocked Next Steps

1. M3-01: standardize docs and terminology on `unique/shared/weak`.
2. M3-02: add parser/type acceptance for `unique<T>`, `shared<T>`, `weak<T>`.
3. M3-03: design compiler-owned prelude or module path that keeps user source
   free of textual include requirements.
