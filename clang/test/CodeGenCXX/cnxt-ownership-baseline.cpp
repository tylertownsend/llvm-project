// RUN: %clang_cc1 -x cnxt -std=cnxt1 -Wno-return-type-c-linkage -emit-llvm -o - %s | FileCheck %s

extern "C" unique<int> pass_unique(unique<int> handle) { return handle; }

extern "C" shared<int> pass_shared(shared<int> handle) { return handle; }

extern "C" weak<int> pass_weak(weak<int> handle) { return handle; }

extern "C" shared<int> lock_weak(weak<int> handle) { return handle.lock(); }

extern "C" int weak_is_expired(weak<int> handle) { return handle.expired(); }

// CHECK: %struct.unique = type { ptr, ptr, ptr, i64, i64 }
// CHECK: %struct.shared = type { ptr, ptr }
// CHECK: %struct.weak = type { ptr, ptr }

// CHECK-LABEL: define{{.*}} @pass_unique(
// CHECK-LABEL: define{{.*}} @pass_shared(
// CHECK-LABEL: define{{.*}} @pass_weak(

// CHECK-LABEL: define{{.*}} @lock_weak(
// CHECK: call {{.*}} @_ZNK4weakIiE4lockEv
// CHECK-LABEL: define linkonce_odr{{.*}} @_ZNK4weakIiE4lockEv(
// CHECK: call ptr @__cnxt_rt_own_v1_weak_lock(ptr

// CHECK-LABEL: define{{.*}} @weak_is_expired(
// CHECK: call {{.*}} @_ZNK4weakIiE7expiredEv
// CHECK-LABEL: define linkonce_odr{{.*}} @_ZNK4weakIiE7expiredEv(
// CHECK: call{{.*}} @__cnxt_rt_own_v1_weak_expired(ptr
