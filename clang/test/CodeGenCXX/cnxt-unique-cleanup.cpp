// RUN: %clang_cc1 -x cnxt -std=cnxt1 -Wno-return-type-c-linkage -emit-llvm -o - %s | FileCheck %s

extern "C" void drop_on_fallthrough(unique<int> input) {
  unique<int> local = static_cast<unique<int> &&>(input);
}

extern "C" void drop_on_return(unique<int> input, int flag) {
  unique<int> local = static_cast<unique<int> &&>(input);
  if (flag)
    return;
}

extern "C" void drop_on_break(unique<int> input) {
  while (1) {
    unique<int> local = static_cast<unique<int> &&>(input);
    break;
  }
}

extern "C" void drop_on_continue(unique<int> input, int flag) {
  while (flag) {
    unique<int> local = static_cast<unique<int> &&>(input);
    flag = 0;
    continue;
  }
}

// CHECK-LABEL: define{{.*}} @drop_on_fallthrough(
// CHECK: call void @_ZN6uniqueIiED1Ev(

// CHECK-LABEL: define{{.*}} @drop_on_return(
// CHECK: call void @_ZN6uniqueIiED1Ev(

// CHECK-LABEL: define{{.*}} @drop_on_break(
// CHECK: call void @_ZN6uniqueIiED1Ev(

// CHECK-LABEL: define{{.*}} @drop_on_continue(
// CHECK: call void @_ZN6uniqueIiED1Ev(

// CHECK-LABEL: define linkonce_odr{{.*}} @_ZN6uniqueIiED2Ev(
// CHECK: call void @_ZN6uniqueIiE5resetEPi(

// CHECK-LABEL: define linkonce_odr{{.*}} @_ZN6uniqueIiE5resetEPi(
// CHECK: call void @__cnxt_rt_own_v1_unique_drop(ptr noundef
