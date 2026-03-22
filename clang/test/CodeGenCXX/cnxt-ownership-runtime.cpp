// RUN: %clang_cc1 -x cnxt -std=cnxt1 -emit-llvm -o - %s | FileCheck %s

unsafe extern "C" void runtime_surface(shared<int> owner, weak<int> observer) {
  shared<int> copied = owner;
  weak<int> aliased(owner);
  shared<int> recovered = observer.lock();
  bool expired = observer.expired();

  copied.reset();

  (void)aliased.expired();
  (void)recovered.get();
  (void)expired;
}

// CHECK-LABEL: define{{.*}} @runtime_surface(
// CHECK: call {{.*}} @_ZN6sharedIiEC1ERKS0_
// CHECK: call {{.*}} @_ZN4weakIiEC1ERK6sharedIiE
// CHECK: call {{.*}} @_ZNK4weakIiE4lockEv
// CHECK: call {{.*}} @_ZNK4weakIiE7expiredEv
// CHECK: call {{.*}} @_ZN6sharedIiE5resetEPi
// CHECK: call {{.*}} @_ZNK6sharedIiE3getEv

// CHECK-LABEL: define linkonce_odr void @_ZNK4weakIiE4lockEv(
// CHECK: call ptr @__cnxt_rt_own_v1_weak_lock(ptr

// CHECK-LABEL: define linkonce_odr noundef zeroext i1 @_ZNK4weakIiE7expiredEv(
// CHECK: call zeroext i8 @__cnxt_rt_own_v1_weak_expired(ptr

// CHECK-LABEL: define linkonce_odr void @_ZN6sharedIiE5resetEPi(
// CHECK: call void @__cnxt_rt_own_v1_shared_release(ptr

// CHECK-LABEL: define linkonce_odr noundef ptr @_ZNK6sharedIiE3getEv(
// CHECK: %View = getelementptr inbounds nuw %struct.shared, ptr %{{.*}}, i32 0, i32 1
// CHECK: %{{.*}} = load ptr, ptr %View, align 8

// CHECK-LABEL: define linkonce_odr void @_ZN6sharedIiEC2ERKS0_(
// CHECK: call void @__cnxt_rt_own_v1_shared_retain(ptr

// CHECK-LABEL: define linkonce_odr void @_ZN4weakIiEC2ERK6sharedIiE(
// CHECK: call void @__cnxt_rt_own_v1_weak_retain(ptr

// CHECK-LABEL: define linkonce_odr void @_ZN4weakIiED2Ev(
// CHECK: call void @__cnxt_rt_own_v1_weak_release(ptr
