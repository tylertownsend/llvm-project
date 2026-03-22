// REQUIRES: native, system-linux
// RUN: rm -rf %t && split-file %s %t
// RUN: %clangxx -shared -fPIC -std=c++17 -I%S/../../../cnxt/runtime/ownership/include %S/../../../cnxt/runtime/ownership/src/ownership_runtime.cpp -o %t/libcnxt_ownership_rt.so
// RUN: %clang -c %t/c-provider.c -o %t/c-provider.o
// RUN: %clangxx -std=c++17 -c %t/cxx-provider.cpp -o %t/cxx-provider.o
// RUN: %clangxx -x cnxt -std=cnxt1 %t/main.cn -x none %t/c-provider.o %t/cxx-provider.o -fcnxt-ownership-runtime=%t/libcnxt_ownership_rt.so -o %t/cnxt-c-abi-mixed-interop
// RUN: env LD_LIBRARY_PATH=%t %t/cnxt-c-abi-mixed-interop | FileCheck %s

// CHECK: mixed c abi interop ok

//--- main.cn
cnxt_import_c int c_add_one(int value);
cnxt_import_c int c_call_cnxt_plus_three(int value);
cnxt_import_c int cxx_double(int value);
cnxt_import_c int cxx_call_cnxt_times_two(int value);

cnxt_export_c int cnxt_plus_three(int value) { return value + 3; }

cnxt_export_c int cnxt_times_two(int value) { return value * 2; }

int main() {
  if (c_add_one(4) != 5)
    return 1;
  if (c_call_cnxt_plus_three(4) != 7)
    return 2;
  if (cxx_double(6) != 12)
    return 3;
  if (cxx_call_cnxt_times_two(6) != 12)
    return 4;

  cnxt::io::println("mixed c abi interop ok");
  return 0;
}

//--- c-provider.c
int cnxt_plus_three(int value);

int c_add_one(int value) { return value + 1; }

int c_call_cnxt_plus_three(int value) { return cnxt_plus_three(value); }

//--- cxx-provider.cpp
extern "C" int cnxt_times_two(int value);

extern "C" int cxx_double(int value) { return value * 2; }

extern "C" int cxx_call_cnxt_times_two(int value) {
  return cnxt_times_two(value);
}
