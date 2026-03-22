// RUN: %clang_cc1 -x cnxt -std=cnxt1 -Wno-return-type-c-linkage -emit-llvm -o - %s | FileCheck %s

extern "C" void drop_constructed_on_return(int flag) {
  unique<int> local = make<int>(42);
  if (flag)
    return;
}

extern "C" void drop_widened_in_branch(int flag) {
  if (flag) {
    shared<int> local = share(make<int>(42));
  }
}

// CHECK-LABEL: define{{.*}} @drop_constructed_on_return(
// CHECK: call void @_Z4makeIiJiEE6uniqueIT_EDpOT0_(
// CHECK: br i1 %{{.*}}, label %[[THEN:[^, ]+]], label %[[ELSE:[^, ]+]]
// CHECK: [[THEN]]:
// CHECK: br label %[[CLEANUP:[^, ]+]]
// CHECK: [[ELSE]]:
// CHECK: br label %[[CLEANUP]]
// CHECK: [[CLEANUP]]:
// CHECK: call void @_ZN6uniqueIiED1Ev(

// CHECK-LABEL: define{{.*}} @drop_widened_in_branch(
// CHECK: br i1 %{{.*}}, label %[[BRANCH:[^, ]+]], label %[[MERGE:[^, ]+]]
// CHECK: [[BRANCH]]:
// CHECK: call void @_Z4makeIiJiEE6uniqueIT_EDpOT0_(
// CHECK: call void @_Z5shareIiE6sharedIT_EO6uniqueIS1_E(
// CHECK: call void @_ZN6uniqueIiED1Ev(
// CHECK: call void @_ZN6sharedIiED1Ev(
// CHECK: br label %[[MERGE]]
// CHECK: [[MERGE]]:
// CHECK: ret void
