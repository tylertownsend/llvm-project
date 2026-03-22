// RUN: %clang_cc1 -x cnxt -std=cnxt1 -Wno-return-type-c-linkage -emit-llvm -o - %s | FileCheck %s

struct Box {
  int value;
  Box(int V) : value(V) {}
};

extern "C" unique<int> make_int() { return make<int>(42); }

extern "C" unique<Box> make_box() { return make<Box>(7); }

// CHECK-LABEL: define{{.*}} @make_int(
// CHECK: call ptr @__cnxt_rt_own_v1_alloc(
// CHECK: store i32 %{{.*}}, ptr %{{.*}}, align 4
// CHECK-LABEL: define{{.*}} @make_box(
// CHECK: call ptr @__cnxt_rt_own_v1_alloc(
// CHECK: call void @_ZN3BoxC1Ei(
