// REQUIRES: system-linux
// RUN: rm -rf %t && mkdir -p %t
// RUN: %clang -shared -fPIC %S/Inputs/cnxt-ownership-runtime-good.c -o %t/libcnxt_ownership_rt_good.so
// RUN: %clang -shared -fPIC %S/Inputs/cnxt-ownership-runtime-noabi.c -o %t/libcnxt_ownership_rt_noabi.so
// RUN: %clang -shared -fPIC %S/Inputs/cnxt-ownership-runtime-badabi.c -o %t/libcnxt_ownership_rt_bad.so
// RUN: not %clang -### -x cnxt -std=cnxt1 %s 2>&1 | FileCheck %s --check-prefix=MISSING
// RUN: not %clang -### -x cnxt -std=cnxt1 %s -fcnxt-ownership-runtime=%t/does-not-exist.so 2>&1 | FileCheck %s --check-prefix=LOAD
// RUN: not %clang -### -x cnxt -std=cnxt1 %s -fcnxt-ownership-runtime=%t/libcnxt_ownership_rt_noabi.so 2>&1 | FileCheck %s --check-prefix=NOABI
// RUN: not %clang -### -x cnxt -std=cnxt1 %s -fcnxt-ownership-runtime=%t/libcnxt_ownership_rt_bad.so 2>&1 | FileCheck %s --check-prefix=BADABI
// RUN: %clang -### -x cnxt -std=cnxt1 %s -fcnxt-ownership-runtime=%t/libcnxt_ownership_rt_good.so 2>&1 | FileCheck %s --check-prefix=GOOD

// MISSING: error: cNxt link requires the ownership runtime; pass '-fcnxt-ownership-runtime=<path>'

// LOAD: error: cannot load cNxt ownership runtime '{{.*}}does-not-exist.so':

// NOABI: error: cNxt ownership runtime '{{.*}}libcnxt_ownership_rt_noabi.so' is missing required ABI symbol '__cnxt_rt_own_v1_abi_version'

// BADABI: error: cNxt ownership runtime '{{.*}}libcnxt_ownership_rt_bad.so' reported unsupported ABI version 7 (expected 1)

// GOOD: "{{[^"]*}}libcnxt_ownership_rt_good.so"

int main(void) { return 0; }
