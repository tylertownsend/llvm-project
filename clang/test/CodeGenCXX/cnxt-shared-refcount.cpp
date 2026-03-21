// RUN: %clang_cc1 -x cnxt -std=cnxt1 -Wno-return-type-c-linkage -emit-llvm -o - %s | FileCheck %s

extern "C" void shared_copy(shared<int> input) {
  shared<int> local = input;
}

extern "C" void shared_move(shared<int> input) {
  shared<int> local = static_cast<shared<int> &&>(input);
}

extern "C" void shared_assign(shared<int> first, shared<int> second) {
  first = second;
}

extern "C" void shared_move_assign(shared<int> first, shared<int> second) {
  first = static_cast<shared<int> &&>(second);
}

// CHECK-LABEL: define{{.*}} @shared_copy(
// CHECK: call void @_ZN6sharedIiEC1ERKS0_(
// CHECK: call void @_ZN6sharedIiED1Ev(

// CHECK-LABEL: define{{.*}} @shared_move(
// CHECK: call void @_ZN6sharedIiEC1EOS0_(
// CHECK: call void @_ZN6sharedIiED1Ev(

// CHECK-LABEL: define{{.*}} @shared_assign(
// CHECK: call{{.*}} @_ZN6sharedIiEaSERKS0_(

// CHECK-LABEL: define linkonce_odr{{.*}} @_ZN6sharedIiEaSERKS0_(
// CHECK: call void @__cnxt_rt_own_v1_shared_retain(ptr noundef
// CHECK: call void @__cnxt_rt_own_v1_shared_release(ptr noundef

// CHECK-LABEL: define{{.*}} @shared_move_assign(
// CHECK: call{{.*}} @_ZN6sharedIiEaSEOS0_(

// CHECK-LABEL: define linkonce_odr{{.*}} @_ZN6sharedIiEaSEOS0_(
// CHECK: call void @__cnxt_rt_own_v1_shared_release(ptr noundef
// CHECK-NOT: __cnxt_rt_own_v1_shared_retain
// CHECK: ret ptr

// CHECK-LABEL: define linkonce_odr{{.*}} @_ZN6sharedIiEC2ERKS0_(
// CHECK: call void @__cnxt_rt_own_v1_shared_retain(ptr noundef

// CHECK-LABEL: define linkonce_odr{{.*}} @_ZN6sharedIiED2Ev(
// CHECK: call void @__cnxt_rt_own_v1_shared_release(ptr noundef

// CHECK-LABEL: define linkonce_odr{{.*}} @_ZN6sharedIiEC2EOS0_(
// CHECK-NOT: __cnxt_rt_own_v1_shared_retain
// CHECK-NOT: __cnxt_rt_own_v1_shared_release
// CHECK: ret void
