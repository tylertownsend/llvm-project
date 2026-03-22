// REQUIRES: native, system-linux
// RUN: rm -rf %t && mkdir -p %t
// RUN: %clangxx -shared -fPIC -std=c++17 -I%S/../../../cnxt/runtime/ownership/include %S/../../../cnxt/runtime/ownership/src/ownership_runtime.cpp -o %t/libcnxt_ownership_rt.so
// RUN: %clangxx -x cnxt -std=cnxt1 %S/../../../cnxt/examples/stdlib/hello-world.cn -fcnxt-ownership-runtime=%t/libcnxt_ownership_rt.so -o %t/cnxt-hello-world
// RUN: env LD_LIBRARY_PATH=%t %t/cnxt-hello-world | FileCheck %s
// CHECK: hello, cnxt
