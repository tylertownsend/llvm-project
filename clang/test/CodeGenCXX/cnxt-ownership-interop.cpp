// RUN: split-file %s %t
// RUN: %clang_cc1 -x cnxt -std=cnxt1 -Wno-return-type-c-linkage -emit-llvm -o - %t/cnxt-api.cn | FileCheck %s --check-prefix=CNXT
// RUN: %clang_cc1 -x c++ -std=c++17 -Wno-return-type-c-linkage -emit-llvm -o - %t/cxx-consumer.cpp | FileCheck %s --check-prefix=CXX

// CNXT: %struct.shared = type { ptr }
// CNXT: %struct.weak = type { ptr }
// CNXT-LABEL: define{{.*}} @cnxt_lock(
// CNXT: call {{.*}} @_ZNK4weakIiE4lockEv
// CNXT-LABEL: define linkonce_odr{{.*}} @_ZNK4weakIiE4lockEv(
// CNXT: call ptr @__cnxt_rt_own_v1_weak_lock(ptr
// CNXT-LABEL: define{{.*}} @cnxt_echo_ptr(
// CNXT-LABEL: define{{.*}} @cnxt_expired(
// CNXT: call {{.*}} @_ZNK4weakIiE7expiredEv
// CNXT-LABEL: define linkonce_odr{{.*}} @_ZNK4weakIiE7expiredEv(
// CNXT: call{{.*}} @__cnxt_rt_own_v1_weak_expired(ptr

// CXX: %"struct.std::shared_ptr" = type { ptr }
// CXX: %"struct.std::weak_ptr" = type { ptr }
// CXX-LABEL: define{{.*}} @use_cnxt_lock(
// CXX: call ptr @cnxt_lock(ptr
// CXX-LABEL: define{{.*}} @use_cnxt_ptr(
// CXX: call ptr @cnxt_echo_ptr(ptr noundef
// CXX-LABEL: define{{.*}} @use_cnxt_expired(
// CXX: call i32 @cnxt_expired(ptr

//--- cnxt-api.cn
extern "C" shared<int> cnxt_lock(weak<int> weak_handle) {
  return weak_handle.lock();
}

unsafe extern "C" int *cnxt_echo_ptr(int *p) { return p; }

extern "C" int cnxt_expired(weak<int> weak_handle) {
  return weak_handle.expired();
}

//--- cxx-consumer.cpp
namespace std {
template <typename T> struct shared_ptr { T *Ptr; };
template <typename T> struct weak_ptr { T *Ptr; };
} // namespace std

extern "C" std::shared_ptr<int> cnxt_lock(std::weak_ptr<int>);
extern "C" int *cnxt_echo_ptr(int *);
extern "C" int cnxt_expired(std::weak_ptr<int>);

extern "C" std::shared_ptr<int> use_cnxt_lock(std::weak_ptr<int> weak_handle) {
  return cnxt_lock(weak_handle);
}

extern "C" int *use_cnxt_ptr(int *p) { return cnxt_echo_ptr(p); }

extern "C" int use_cnxt_expired(std::weak_ptr<int> weak_handle) {
  return cnxt_expired(weak_handle);
}
