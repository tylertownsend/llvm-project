# cNxt Quickstart: No Manual `extern "C"` Glue

This quickstart shows the branch-local path for running ordinary cNxt programs
without handwritten `extern "C"` wrappers, raw-pointer allocation syntax, or
separate glue files.

It uses the same starter fixture and examples that the repository already tests.

## Prerequisites

Build the cNxt-enabled `clang++` once:

```bash
cmake -S llvm -B build -G Ninja \
  -DLLVM_ENABLE_PROJECTS=clang \
  -DCMAKE_BUILD_TYPE=Release

cmake --build build --parallel --target clang
```

The commands below assume the compiler is available at `build/bin/clang++`.

## 1. Run the Starter App

The starter fixture mirrors the intended `cnxt new` layout:

```text
cnxt/examples/starter/hello-app/
├── Cnxt.toml
└── src/main.cn
```

Run it through the package tool:

```bash
python3 cnxt/tools/cnxt_run.py cnxt/examples/starter/hello-app \
  --skip-fetch \
  --compiler build/bin/clang++
```

Expected output:

```text
hello, cnxt
```

The starter source is intentionally small:

```cnxt
int main() {
  cnxt::io::println("hello, cnxt");
  return 0;
}
```

There is no user-written FFI surface in that app.

You can confirm that directly:

```bash
rg -n 'extern "C"|unsafe extern' cnxt/examples/starter/hello-app
```

Expected result: no matches.

## 2. Try Owned Heap Construction Without Glue

The repository also includes a no-glue ownership sample:

```bash
build/bin/clang++ -shared -fPIC -std=c++17 \
  -Icnxt/runtime/ownership/include \
  cnxt/runtime/ownership/src/ownership_runtime.cpp \
  -o /tmp/libcnxt_ownership_rt.so

build/bin/clang++ -x cnxt -std=cnxt1 \
  cnxt/examples/ownership/class-method.cn \
  -fcnxt-ownership-runtime=/tmp/libcnxt_ownership_rt.so \
  -o /tmp/cnxt-class-method

LD_LIBRARY_PATH=/tmp /tmp/cnxt-class-method
```

This example uses `make<T>(...)` and `unique<T>` with no handwritten ABI glue.

## 3. Try Interface Dispatch Without Glue

The interface example stays on the same no-glue path:

```bash
build/bin/clang++ -shared -fPIC -std=c++17 \
  -Icnxt/runtime/ownership/include \
  cnxt/runtime/ownership/src/ownership_runtime.cpp \
  -o /tmp/libcnxt_ownership_rt.so

build/bin/clang++ -x cnxt -std=cnxt1 \
  cnxt/examples/ownership/interface-counter.cn \
  -fcnxt-ownership-runtime=/tmp/libcnxt_ownership_rt.so \
  -o /tmp/cnxt-interface-counter

LD_LIBRARY_PATH=/tmp /tmp/cnxt-interface-counter
```

That sample allocates a concrete class, stores it as `unique<Stepper>`, and
dispatches interface calls without `extern "C"` shims or raw-pointer syntax in
user code.

You can confirm the shipped examples stay glue-free:

```bash
rg -n 'extern "C"|unsafe extern' \
  cnxt/examples/ownership/class-method.cn \
  cnxt/examples/ownership/interface-counter.cn
```

Expected result: no matches.

## 4. What Still Requires `unsafe extern "C"`

Normal app code on this branch does not need manual C ABI glue for:

- hello-world/stdout
- `make<T>(...)` construction
- `unique/shared/weak`
- `interface` + `class` dispatch
- compiler-managed C ABI import/export through `cnxt_import_c` /
  `cnxt_export_c`

You still need `unsafe extern "C"` only when a boundary genuinely exchanges raw
addresses or raw-pointer-bearing structs.

For that path, see:

- `cnxt/docs/c-abi-migration.md`
- `cnxt/specs/cnxt-ffi-boundary.md`

## 5. Why This Counts as "No Glue"

The quickstart path above avoids all of the following in user code:

- handwritten `extern "C"` wrappers
- separate adapter translation units
- raw `new` / `delete`
- raw pointer fields or signatures in safe modules
- manual runtime staging for `cnxt run`

The current branch still has an explicit `-fcnxt-ownership-runtime=...` flag
when invoking `clang++` directly, but the package-tool starter flow hides that
detail from ordinary app execution.
