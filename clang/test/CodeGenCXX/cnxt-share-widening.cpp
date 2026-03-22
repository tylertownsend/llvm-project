// RUN: %clang_cc1 -x cnxt -std=cnxt1 -Wno-return-type-c-linkage -emit-llvm -o - %s | FileCheck %s

struct Box {
  int value;
  Box(int V) : value(V) {}
  ~Box() {}
};

extern "C" shared<int> widen_int(unique<int> input) {
  return share(static_cast<unique<int> &&>(input));
}

extern "C" shared<Box> widen_box(unique<Box> input) {
  return share(static_cast<unique<Box> &&>(input));
}

// CHECK-LABEL: define{{.*}} @widen_int(
// CHECK: call void @_Z5shareIiE6sharedIT_EO6uniqueIS1_E(

// CHECK-LABEL: define linkonce_odr void @_Z5shareIiE6sharedIT_EO6uniqueIS1_E(
// CHECK: call noundef ptr @_ZNK6uniqueIiE6__viewEv(
// CHECK: call noundef ptr @_ZNK6uniqueIiE6__dtorEv(
// CHECK: call noundef i64 @_ZNK6uniqueIiE6__sizeEv(
// CHECK: call noundef i64 @_ZNK6uniqueIiE7__alignEv(
// CHECK: call noundef ptr @_ZN6uniqueIiE17__release_storageEv(
// CHECK: call ptr @__cnxt_rt_own_v1_shared_from_unique(
// CHECK: call void @_ZN6sharedIiEC1EPvPii(

// CHECK-LABEL: define{{.*}} @widen_box(
// CHECK: call void @_Z5shareI3BoxE6sharedIT_EO6uniqueIS2_E(

// CHECK-LABEL: define linkonce_odr void @_Z5shareI3BoxE6sharedIT_EO6uniqueIS2_E(
// CHECK: call noundef ptr @_ZNK6uniqueI3BoxE6__viewEv(
// CHECK: call noundef ptr @_ZNK6uniqueI3BoxE6__dtorEv(
// CHECK: call noundef i64 @_ZNK6uniqueI3BoxE6__sizeEv(
// CHECK: call noundef i64 @_ZNK6uniqueI3BoxE7__alignEv(
// CHECK: call noundef ptr @_ZN6uniqueI3BoxE17__release_storageEv(
// CHECK: call ptr @__cnxt_rt_own_v1_shared_from_unique(
// CHECK: call void @_ZN6sharedI3BoxEC1EPvPS0_i(
