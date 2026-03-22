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
// CHECK: call noundef ptr @_ZN6uniqueIiE7releaseEv(
// CHECK: call noundef ptr @_Z19__cnxt_payload_dtorIiEPFvPvEv()
// CHECK: call ptr @__cnxt_rt_own_v1_shared_from_unique(

// CHECK-LABEL: define{{.*}} @widen_box(
// CHECK: call void @_Z5shareI3BoxE6sharedIT_EO6uniqueIS2_E(

// CHECK-LABEL: define linkonce_odr void @_Z5shareI3BoxE6sharedIT_EO6uniqueIS2_E(
// CHECK: call noundef ptr @_ZN6uniqueI3BoxE7releaseEv(
// CHECK: call noundef ptr @_Z19__cnxt_payload_dtorI3BoxEPFvPvEv()
// CHECK: call ptr @__cnxt_rt_own_v1_shared_from_unique(

// CHECK-LABEL: define linkonce_odr noundef ptr @_Z19__cnxt_payload_dtorIiEPFvPvEv()
// CHECK: ret ptr null

// CHECK-LABEL: define linkonce_odr noundef ptr @_Z19__cnxt_payload_dtorI3BoxEPFvPvEv()
// CHECK: ret ptr @_Z22__cnxt_destroy_payloadI3BoxEvPv
