# cNxt Ownership Runtime Skeleton

This directory contains the Milestone 6 baseline skeleton implementation for
the cNxt ownership runtime ABI (`__cnxt_rt_own_v1_*`).

Build example:

```bash
cmake -S cnxt/runtime/ownership -B build-cnxt-ownership
cmake --build build-cnxt-ownership
```

Produced library target:

- `cnxt_ownership_rt` (`libcnxt_ownership_rt.so.1`)

Sanitizer/stress test example:

```bash
cmake -S cnxt/runtime/ownership -B build-cnxt-ownership-sanitizers \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_CXX_COMPILER=c++ \
  -DBUILD_TESTING=ON \
  -DCNXT_OWNERSHIP_RT_ENABLE_SANITIZERS=ON

cmake --build build-cnxt-ownership-sanitizers --parallel
ctest --test-dir build-cnxt-ownership-sanitizers --output-on-failure
```

The sanitizer suite covers clean lifecycle, `weak_lock` contention stress,
leak detection, use-after-free detection, and double-free detection.
