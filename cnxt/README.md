# cNxt Design

## Why this fork starts from LLVM/Clang

cNxt should be a language fork, not a permanent divergence from upstream LLVM.
LLVM/Clang is the right base because the frontend, driver, diagnostics, clangd,
and LLVM IR pipeline are already separated cleanly enough to let us replace the
language surface while keeping the optimizer, linker, debugger, and tooling.

The fork strategy is:

1. Keep upstream LLVM history intact and track `upstream/main`.
2. Keep all cNxt-specific code additive where possible under new paths such as
   `cnxt/`, `clang/lib/CNxt/`, and `clang/include/clang/CNxt/`.
3. Keep invasive edits limited to language registration, parser dispatch,
   semantic restriction points, and tooling integration.
4. Prefer a small set of stable hooks over broad rewrites so rebasing onto new
   LLVM releases stays practical.

## Product goal

cNxt is a new language that borrows C's directness and data layout, uses modern
C++ code generation and runtime support, and removes most of the feature surface
that makes C++ hard to teach, analyze, and tool.

The language should feel like:

- C-style structs, enums, free functions, and predictable control flow.
- Functional-first semantics: immutable by default, explicit mutation, explicit
  effects, no hidden ownership.
- Managed memory by default using language-level ownership handles.
- One obvious way to write common code.
- Modules and packages by default, not headers and textual includes.
- Excellent IDE support because the language does not depend on macros,
  textual inclusion, ad hoc build scripts, or template metaprogramming.

## Non-goals for v1

- Full C++ source compatibility.
- Header-based libraries.
- User-defined templates or template metaprogramming.
- Exceptions, RTTI, multiple inheritance, operator overloading, or macros.
- The many parallel ways C++ offers to express the same loop, ownership model,
  or generic abstraction.

## cNxt v1 language model

### Core declarations

Only these top-level constructs are supported in v1:

- `import`
- `fn`
- `struct`
- `enum`
- `const`
- `type`
- `extern`
- `test`

Classes, inheritance, namespaces, macros, and headers are not part of cNxt
source. Internally we can still lower to Clang AST nodes that already exist.

### Control flow

To keep the language "Go-like" in consistency, v1 should allow only:

- `if` / `else`
- `match` for tagged unions and enums
- `for item in expr`
- `while expr`
- `defer`
- `return`
- `break`
- `continue`

Explicitly rejected in v1:

- C-style `for (;;)`
- `do/while`
- `goto`
- exception-based control flow

This gives us a narrow grammar and much better linting, formatting, and code
completion behavior.

### Ownership and memory

The default data model is:

- Values live on the stack by default.
- Heap allocation is explicit.
- Owning raw pointers do not exist in safe code.
- Raw pointers are allowed only in `unsafe` FFI boundaries.

v1 handle types:

- `unique<T>`: move-only owning heap handle.
- `shared<T>`: reference-counted shared ownership.
- `weak<T>`: non-owning weak reference to a `shared<T>`.
- `ptr<T>`: non-owning raw pointer for `unsafe` and FFI only.

This is intentionally smaller than C++. The standard library may implement
these handles on top of libc++ primitives initially, but the language surface
is cNxt-owned and enforced by the compiler.

### Functional-first semantics

The design target is a functional-first language, with explicit escape hatches
instead of ambient mutation.

Rules for v1:

- Bindings are immutable unless declared `var`.
- Function arguments are immutable.
- Global mutable state is rejected outside runtime internals.
- Heap mutation requires a mutable handle.
- Side-effecting APIs are marked in the standard library and easy to lint.

This is stricter than C++ but still practical to implement on top of Clang.

### Iteration

Iterators are supported, but only one surface form is legal:

```cnxt
for item in items {
    use(item)
}
```

The compiler should define one iterator protocol for v1:

- `iter(expr)` creates an iterator value.
- `next(it)` returns `option<T>`.

Internally, the first implementation can lower `for item in expr` through the
existing range-for machinery in Clang and later switch to a dedicated cNxt loop
node if that becomes cleaner.

### Modules and packages

cNxt should not support textual includes in user code.

v1 package layout:

```text
Cnxt.toml
src/main.cn
src/lib.cn
tests/
```

Package manager commands:

- `cnxt new`
- `cnxt build`
- `cnxt run`
- `cnxt test`
- `cnxt fmt`
- `cnxt lsp`

Outputs:

- `target/debug/...`
- `target/release/...`
- generated `compile_commands.json` for clangd compatibility

## Compiler implementation plan

### Phase 0: fork shape and branch model

Repository state:

- clone upstream `llvm-project`
- create local branch `cnxt/main`
- add a fork-specific top-level directory `cnxt/`

Recommended remote model once a hosted fork exists:

- `upstream` -> official LLVM repo
- `origin` -> cNxt fork

Recommended update workflow:

1. sync `upstream/main`
2. rebase or merge into `cnxt/main`
3. run cNxt language tests, clang tests, and clangd tests
4. keep cNxt patches grouped by subsystem so conflicts stay localized

### Phase 1: register a new language in Clang

Detailed write-up: `cnxt/docs/milestone-1.md`

Primary touchpoints already identified in this tree:

- `clang/include/clang/Basic/LangStandard.h`
- `clang/include/clang/Basic/LangStandards.def`
- `clang/lib/Basic/LangStandards.cpp`
- `clang/lib/Basic/LangOptions.cpp`
- `clang/include/clang/Frontend/FrontendOptions.h`
- `clang/lib/Frontend/CompilerInvocation.cpp`
- `clang/include/clang/Driver/Types.def`
- `clang/lib/Driver/Types.cpp`
- `clang/lib/Tooling/InterpolatingCompilationDatabase.cpp`
- `clang-tools-extra/clangd/SourceCode.cpp`

Concrete changes:

1. Add `Language::CNxt`.
2. Add `-x cnxt`.
3. Add a file type for `.cn` and `.cnxt`.
4. Add `-std=cnxt1`.
5. Make `cnxt1` the default standard when the input language is `CNxt`.
6. Add `LangOptions` flags such as:
   - `CNxt`
   - `CNxtManagedMemory`
   - `CNxtNoExceptions`
   - `CNxtNoTemplates`
   - `CNxtNoRawOwningPointers`
   - `CNxtSingleLoopForms`

This gives us language mode selection without yet changing the parser heavily.

### Phase 2: start as a restricted C++ subset with strong diagnostics

Detailed write-up: `cnxt/docs/milestone-2.md`

The fastest path to a working compiler is not "invent a brand new frontend" but
"use the Clang C++ frontend as a host, then prohibit most of C++."

Initial parsing approach:

- accept a deliberately small C++-derived core
- reject unsupported constructs in parser/sema with cNxt-specific diagnostics
- lower cNxt `for in` through existing range-for support first

Primary restriction points:

- `clang/lib/Parse/ParseStmt.cpp`
- `clang/lib/Parse/ParseDecl.cpp`
- `clang/lib/Parse/ParseExpr.cpp`
- `clang/lib/Parse/ParseExprCXX.cpp`
- `clang/lib/Sema/SemaStmt.cpp`
- `clang/lib/Sema/SemaDecl.cpp`
- `clang/lib/Sema/SemaExpr.cpp`
- `clang/lib/Sema/SemaOverload.cpp`

Examples of features to reject in v1:

- templates
- overloaded operators
- exceptions
- inheritance
- `new` / `delete`
- `goto`
- C-style casts outside `unsafe`
- C-style `for`
- macros in user packages

This phase gets a useful compiler and language server early.

### Phase 3: add cNxt surface syntax

Once the restriction mode is stable, add cNxt-native spellings:

- `fn` instead of C++ function declarations
- `let` / `var`
- `import` instead of includes
- `match`
- `defer`
- cNxt ownership types and allocation forms

Implementation strategy:

- keep the lexer and token stream in Clang
- add cNxt parser entry points under `clang/lib/CNxt/` or adjacent parser files
- translate cNxt syntax into existing AST nodes where possible
- introduce dedicated AST nodes only where existing Clang nodes impose C++
  semantics we do not want

The important constraint is to avoid a wholesale rewrite of AST and CodeGen.

### Phase 4: ownership-aware semantics

This is the feature that makes cNxt a different language instead of a style
guide.

Compiler responsibilities:

- disallow implicit raw owning pointers in safe code
- track handle conversions `unique -> shared -> weak`
- reject unsafe aliasing in safe code
- require explicit `unsafe` for raw pointer arithmetic and FFI memory access
- prefer deterministic destruction over tracing GC

Runtime responsibilities:

- `libcnxt_core`: handles, option/result, strings, containers, iterator traits
- `libcnxt_alloc`: allocation and reference counting runtime
- `libcnxt_ffi`: C ABI interop

Do not fork libc++ more than necessary. Build `libcnxt` on top of libc++ first,
then replace internals only if profiling proves it necessary.

### Phase 5: modules and package manager

This should be a new tool, not a pile of driver flags.

Add a top-level tool:

- `clang/tools/cnxt/` or `cnxt/tool/`

Responsibilities:

- parse `Cnxt.toml`
- resolve dependencies
- build a package graph
- invoke the compiler with stable arguments
- write `compile_commands.json`
- expose package metadata to clangd

Cargo-like behavior we want:

- reproducible dependency resolution
- lockfile by default
- standard source layout
- named profiles
- build graph and diagnostics that are machine-readable

### Phase 6: clangd and IDE support

The cNxt language story is only credible if IDE support ships with the compiler.

Existing integration points:

- `clang-tools-extra/clangd/SourceCode.cpp`
- `clang-tools-extra/clangd/CompileCommands.cpp`
- `clang/lib/Tooling/InterpolatingCompilationDatabase.cpp`

Required work:

1. Recognize `.cn` and `.cnxt`.
2. Teach fallback compile command generation to use `-x cnxt`.
3. Make the package manager emit canonical compile commands.
4. Add semantic tokens, hover, completion, and inlay hints for cNxt-only
   constructs.

Because cNxt bans macros, headers, and template metaprogramming in user code,
clangd should be substantially more predictable than for full C++.

## Build and distribution shape

The first supported pipeline should be:

```text
cnxt build
  -> cnxt package graph
  -> clang frontend in cNxt mode
  -> LLVM IR
  -> lld
  -> executable / library
```

Do not invent a new backend, linker, or debugger.

## Suggested directory layout for fork-specific code

```text
cnxt/
  README.md
  docs/
  specs/
clang/include/clang/CNxt/
clang/lib/CNxt/
clang/tools/cnxt/
libcnxt/
```

This keeps new code mostly additive and lowers merge risk with upstream.

## Roadmap

### Milestone 1: language mode and driver plumbing

- `-x cnxt`
- `.cn` / `.cnxt`
- `-std=cnxt1`
- basic compile and diagnostics

Detailed write-up: `cnxt/docs/milestone-1.md`

### Milestone 2: restricted subset compiler

- reject unsupported C++ features
- support `fn`, `struct`, `enum`, `let`, `var`
- support `for in`, `while`, `if`, `defer`

### Milestone 3: ownership runtime

- `unique/shared/weak`
- safe heap allocation APIs
- `unsafe` FFI boundary

### Milestone 4: package manager

- `Cnxt.toml`
- dependency resolution
- `build`, `run`, `test`

### Milestone 5: IDE quality

- clangd support
- formatter
- lints enforcing the "one obvious way" rule set

## Recommendation

Start cNxt as a strict, intentionally small language mode hosted inside Clang,
not as a brand-new compiler. The first year should optimize for a coherent
language surface, deterministic builds, and strong tooling, not for feature
count.

That means:

- one language standard: `cnxt1`
- one package layout
- one iterator surface form
- one ownership vocabulary
- one blessed build tool

If we hold that line, cNxt can stay close enough to upstream LLVM to keep
rebasing feasible while still becoming a meaningfully better language for modern
tooling.
