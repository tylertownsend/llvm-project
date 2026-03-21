// RUN: %clang_cc1 -x cnxt -std=cnxt1 -Wno-return-type-c-linkage -emit-llvm -o - %s | FileCheck %s

extern "C" int default_weak_lock_is_null() {
  weak<int> observer;
  return observer.lock().get() == nullptr;
}

extern "C" int default_weak_is_expired() {
  weak<int> observer;
  return observer.expired();
}

// CHECK-LABEL: define{{.*}} @default_weak_lock_is_null(
// CHECK: call void @_ZN4weakIiEC1Ev(
// CHECK: call void @_ZNK4weakIiE4lockEv(
// CHECK: call{{.*}} @_ZNK6sharedIiE3getEv(
// CHECK: icmp eq ptr {{.*}}, null

// CHECK-LABEL: define linkonce_odr{{.*}} @_ZNK4weakIiE4lockEv(
// CHECK: call ptr @__cnxt_rt_own_v1_weak_lock(ptr noundef

// CHECK-LABEL: define linkonce_odr{{.*}} @_ZNK6sharedIiE3getEv(
// CHECK: call ptr @__cnxt_rt_own_v1_shared_get(ptr noundef

// CHECK-LABEL: define{{.*}} @default_weak_is_expired(
// CHECK: call void @_ZN4weakIiEC1Ev(
// CHECK: call{{.*}} @_ZNK4weakIiE7expiredEv(

// CHECK-LABEL: define linkonce_odr{{.*}} @_ZNK4weakIiE7expiredEv(
// CHECK: call zeroext i8 @__cnxt_rt_own_v1_weak_expired(ptr noundef
// CHECK: icmp ne i32 {{.*}}, 0

// CHECK-LABEL: define linkonce_odr{{.*}} @_ZN4weakIiEC2Ev(
// CHECK: store ptr null, ptr
