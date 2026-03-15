# cNxt Milestone 1

## Goal

Milestone 1 creates a real compiler entry point for cNxt inside Clang without
yet changing the language grammar in a major way.

When this milestone is complete, the fork should support:

- source files ending in `.cn` and `.cnxt`
- explicit language selection with `-x cnxt`
- a language standard name `-std=cnxt1`
- default language standard selection for cNxt inputs
- end-to-end driver, frontend, tooling, and clangd recognition of cNxt files
- stable diagnostics that clearly identify the input as cNxt

This milestone is about plumbing and identity. It is not yet about the full
surface syntax of the language.

## Why this milestone exists

Before we add ownership rules, package management, or cNxt-native syntax, the
fork needs a first-class language mode. Without that, every later change stays
fragile because the driver, frontend, tooling, and language server still treat
cNxt as "some form of C++ with conventions."

Milestone 1 gives us:

- a canonical way to invoke the compiler
- a stable file extension story
- a stable `LangOptions` mode bit for downstream restrictions
- testable integration points for clang tools and clangd
- a clean branch for later parser and semantic work

## Scope

### In scope

- add a new language kind `CNxt`
- add a new standard `cnxt1`
- map `.cn` and `.cnxt` to cNxt in the driver
- add `-x cnxt`
- make cNxt participate in compile command inference and clangd file handling
- add minimal frontend diagnostics and tests proving the mode is wired
- add fork-owned `LangOptions` flags that later milestones can consume

### Out of scope

- cNxt-only keywords such as `fn`, `let`, `var`, `match`, or `defer`
- ownership checking
- package manager implementation
- custom runtime libraries
- code generation changes beyond what is needed to carry the new language mode
- formatter or linter work

## User-visible behavior

After Milestone 1, these invocations should work:

```bash
clang -x cnxt -std=cnxt1 -c hello.cn
clang -c hello.cn
clangd hello.cn
```

Expected behavior:

- `hello.cn` is treated as cNxt input by default.
- `-std=cnxt1` is accepted when the input is cNxt.
- `clang -x cnxt` works even for files without a cNxt extension.
- unsupported cNxt syntax still fails, but the compiler is clearly in cNxt mode.

## Design constraints

Milestone 1 should stay rebasing-friendly.

That means:

- prefer additive enum and switch updates over broad refactors
- avoid introducing large new subsystems
- do not fork the parser yet unless language mode dispatch requires a tiny hook
- keep cNxt behavior centralized in a few obvious files
- add tests for each touched subsystem so future LLVM rebases catch regressions

## Workstreams

### 1. Language registration

Purpose:

- make cNxt a first-class frontend language

Primary files:

- `clang/include/clang/Basic/LangStandard.h`
- `clang/include/clang/Basic/LangStandards.def`
- `clang/lib/Basic/LangStandards.cpp`
- `clang/lib/Basic/LangOptions.cpp`
- `clang/include/clang/Basic/LangOptions.h`
- `clang/include/clang/Basic/LangOptions.def`

Required changes:

1. Add `Language::CNxt` to the language enum.
2. Extend `languageToString()` to print `cNxt`.
3. Add `LANGSTANDARD(cnxt1, "cnxt1", CNxt, ...)` to
   `clang/include/clang/Basic/LangStandards.def`.
4. Make `getDefaultLanguageStandard()` return `lang_cnxt1` for `Language::CNxt`.
5. Add `LangOptions` mode bits:
   - `CNxt`
   - `CNxtManagedMemory`
   - `CNxtNoExceptions`
   - `CNxtNoTemplates`
   - `CNxtNoRawOwningPointers`
   - `CNxtSingleLoopForms`
6. In `LangOptions::setLangDefaults()`, turn these on by default for cNxt.

Important rule:

- `cnxt1` should not advertise GNU mode or accidental C++ compatibility flags.

### 2. Frontend invocation and `-std=` parsing

Purpose:

- make the frontend accept cNxt mode from command-line arguments

Primary files:

- `clang/include/clang/Frontend/FrontendOptions.h`
- `clang/lib/Frontend/CompilerInvocation.cpp`

Required changes:

1. Teach `InputKind` serialization and parsing about `Language::CNxt`.
2. Make `CompilerInvocation` print `-x cnxt` back out when replaying commands.
3. Accept `-std=cnxt1` in `LangStandard::getLangKind()`.
4. Ensure `IsInputCompatibleWithStandard()` treats cNxt inputs as compatible
   only with `cnxt1`.
5. Ensure invalid combinations such as `-x c++ -std=cnxt1` or
   `-x cnxt -std=c++20` produce direct diagnostics.

Acceptance detail:

- command replay from `CompilerInvocation` should preserve cNxt mode.

### 3. Driver type system and extension mapping

Purpose:

- make the driver recognize cNxt source files before frontend startup

Primary files:

- `clang/include/clang/Driver/Types.def`
- `clang/include/clang/Driver/Types.h`
- `clang/lib/Driver/Types.cpp`
- `clang/lib/Driver/Driver.cpp`

Required changes:

1. Add new driver type IDs for cNxt source and preprocessed cNxt source.
2. Map `.cn` and `.cnxt` to the cNxt source type in
   `lookupTypeForExtension()`.
3. Add `cnxt` as a user-visible `-x` spelling through `Types.def`.
4. Ensure `isSrcFile()`, `isAcceptedByClang()`, and related helpers treat cNxt
   like a frontend source language.
5. Ensure driver jobs route cNxt through preprocess, compile, backend,
   assemble, and link phases like other C-family languages.

Important non-goal:

- do not add a separate `cnxt++` or alternate dialect in Milestone 1.

### 4. Tooling and compile database integration

Purpose:

- keep libTooling and compile command inference aligned with the new language

Primary files:

- `clang/lib/Tooling/InterpolatingCompilationDatabase.cpp`
- `clang/lib/Tooling/CommonOptionsParser.cpp`

Required changes:

1. Make filename-based type guessing recognize `.cn` and `.cnxt`.
2. Ensure fallback language folding does not collapse cNxt into C or C++.
3. Preserve `-x cnxt` and `-std=cnxt1` in inferred or replayed compile commands.

Acceptance detail:

- libTooling should be able to open a standalone `.cn` file with a sensible
  fallback compile command.

### 5. clangd support

Purpose:

- keep editor support viable from the first compiler milestone

Primary files:

- `clang-tools-extra/clangd/SourceCode.cpp`
- `clang-tools-extra/clangd/CompileCommands.cpp`
- `clang-tools-extra/clangd/GlobalCompilationDatabase.*`

Required changes:

1. Recognize `.cn` and `.cnxt` as source files, not unknown files.
2. Ensure header detection logic does not misclassify cNxt files.
3. Make fallback compile command generation choose `-x cnxt`.
4. Preserve `-std=cnxt1` when clangd builds a `CompilerInvocation`.

Acceptance detail:

- opening a standalone `.cn` file in clangd should produce parse diagnostics
  from cNxt mode instead of "unknown file type" or default C++ behavior.

### 6. Minimal diagnostics

Purpose:

- make cNxt mode visible and debuggable for users and for later milestones

Primary files:

- `clang/include/clang/Basic/DiagnosticFrontendKinds.td`
- `clang/include/clang/Basic/DiagnosticDriverKinds.td`
- `clang/include/clang/Basic/DiagnosticParseKinds.td`

Required changes:

- add direct diagnostics for:
  - invalid `-std=` value combinations involving cNxt
  - unsupported parser features once cNxt mode is active
  - any Milestone 1 "recognized language but not yet implemented" failure path

Important rule:

- do not leave users with generic C++ diagnostics if the real issue is that a
  cNxt feature is not implemented yet.

## Suggested implementation order

1. Add `Language::CNxt` and `lang_cnxt1`.
2. Add `LangOptions` defaults for cNxt.
3. Add driver types and extension mapping for `.cn` and `.cnxt`.
4. Add `-x cnxt` support and `CompilerInvocation` round-tripping.
5. Add libTooling and clangd extension support.
6. Add tests for driver, frontend, and clangd behavior.
7. Add minimal cNxt-specific diagnostics.

This order gets CLI usability first and editor usability immediately after.

## Detailed acceptance criteria

Milestone 1 is complete only when all of the following are true.

### Driver and frontend

- `clang -x cnxt -std=cnxt1 -### test.cn` shows cNxt input selection.
- `clang -c test.cn` infers cNxt mode from the extension.
- `clang -x cnxt -std=c++20 test.cn` fails with a cNxt-specific compatibility
  diagnostic.
- `clang -x c++ -std=cnxt1 test.cc` fails with a language/standard mismatch
  diagnostic.
- `CompilerInvocation` round-trips the language as `cnxt`.

### Tooling

- libTooling fallback compile commands recognize `.cn`.
- `compile_commands.json` entries using `-x cnxt` replay correctly.

### clangd

- clangd can open `.cn` and `.cnxt` files without treating them as unknown.
- clangd fallback commands select cNxt mode.

### Tests

- new driver tests under `clang/test/Driver/`
- new frontend/invocation tests under `clang/test/Frontend/`
- new tooling or clangd tests where needed under
  `clang-tools-extra/clangd/unittests/`

## Proposed tests

### Driver tests

Add tests covering:

- `.cn` extension mapping
- `.cnxt` extension mapping
- `-x cnxt`
- `-std=cnxt1`
- invalid `-std=` combinations

### Frontend tests

Add tests covering:

- `CompilerInvocation` serialization of `-x cnxt`
- default standard selection for `Language::CNxt`
- `LangOptions` defaults specific to cNxt

### clangd tests

Add tests covering:

- source file type inference
- fallback compile command for `.cn`
- compile command replay preserving cNxt mode

## Risks

### Risk: cNxt is treated as "just C++ with another extension"

Mitigation:

- add a real language enum
- add a real standard name
- add dedicated `LangOptions` bits

### Risk: merge conflicts from touching too many core frontend files

Mitigation:

- keep changes minimal and localized
- prefer switch additions over refactors
- keep cNxt-specific diagnostics and flags grouped

### Risk: clangd and tooling silently fall back to C++

Mitigation:

- test both extension-based inference and explicit `-x cnxt`
- add unit coverage around compile command generation

## Deliverables

At the end of Milestone 1, the fork should contain:

- new cNxt language enum and standard registration
- new driver type mapping for `.cn` and `.cnxt`
- cNxt-specific `LangOptions`
- cNxt-aware `CompilerInvocation`
- cNxt-aware libTooling and clangd behavior
- tests proving the above

## Explicitly deferred to Milestone 2

Milestone 2 starts only after Milestone 1 is stable.

Deferred items:

- `fn`, `let`, `var`, `match`, `defer`
- C++ restriction diagnostics beyond what is necessary for language identity
- loop-shape enforcement
- ownership semantics
- runtime library design

## Recommendation

Implement Milestone 1 as infrastructure only. Resist the temptation to start
adding syntax in the same patch series. A clean cNxt language mode with strong
tests is the foundation that keeps every later milestone maintainable.
