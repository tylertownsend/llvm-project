// RUN: %clang_cc1 -x cnxt -std=cnxt1 -emit-llvm -o - %s | FileCheck %s

extern "C" void runtime_surface(shared<int> owner, weak<int> observer) {
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

// CHECK-DAG: call void @__cnxt_rt_own_v1_shared_retain(ptr
// CHECK-DAG: call void @__cnxt_rt_own_v1_weak_retain(ptr
// CHECK-DAG: call ptr @__cnxt_rt_own_v1_weak_lock(ptr
// CHECK-DAG: call{{.*}} @__cnxt_rt_own_v1_weak_expired(ptr
// CHECK-DAG: call ptr @__cnxt_rt_own_v1_shared_get(ptr
// CHECK-DAG: call void @__cnxt_rt_own_v1_shared_release(ptr
// CHECK-DAG: call void @__cnxt_rt_own_v1_weak_release(ptr
