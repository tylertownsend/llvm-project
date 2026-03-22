// RUN: split-file %s %t
// RUN: %clang_cc1 -x cnxt -std=cnxt1 -Wno-return-type-c-linkage -emit-llvm -o - %t/export.cn | FileCheck %s --check-prefix=EXPORT
// RUN: %clang_cc1 -x cnxt -std=cnxt1 -emit-llvm -o - %t/import.cn | FileCheck %s --check-prefix=IMPORT
// RUN: %clang_cc1 -x c++ -std=c++17 -Wno-return-type-c-linkage -emit-llvm -o - %t/cxx-consumer.cpp | FileCheck %s --check-prefix=CXX

// EXPORT: %struct.shared = type { ptr, ptr }
// EXPORT: %struct.weak = type { ptr, ptr }
// EXPORT-LABEL: define{{.*}} @cnxt_lock(
// EXPORT: call {{.*}} @_ZNK4weakIiE4lockEv
// EXPORT-LABEL: define{{.*}} @cnxt_expired(
// EXPORT: call {{.*}} @_ZNK4weakIiE7expiredEv

// IMPORT-LABEL: define{{.*}} @_Z13call_importedv(
// IMPORT: call noundef i32 @c_increment(i32 noundef 41)

// CXX-LABEL: define{{.*}} @use_cnxt_lock(
// CXX: call ptr @cnxt_lock(ptr
// CXX-LABEL: define{{.*}} @use_cnxt_expired(
// CXX: call i32 @cnxt_expired(ptr

//--- export.cn
cnxt_export_c shared<int> cnxt_lock(weak<int> weak_handle) {
  return weak_handle.lock();
}

cnxt_export_c int cnxt_expired(weak<int> weak_handle) {
  return weak_handle.expired();
}

//--- import.cn
cnxt_import_c int c_increment(int value);

int call_imported() {
  return c_increment(41);
}

//--- cxx-consumer.cpp
namespace std {
template <typename T> struct shared_ptr { T *Ptr; };
template <typename T> struct weak_ptr { T *Ptr; };
} // namespace std

extern "C" std::shared_ptr<int> cnxt_lock(std::weak_ptr<int>);
extern "C" int cnxt_expired(std::weak_ptr<int>);

extern "C" std::shared_ptr<int> use_cnxt_lock(std::weak_ptr<int> weak_handle) {
  return cnxt_lock(weak_handle);
}

extern "C" int use_cnxt_expired(std::weak_ptr<int> weak_handle) {
  return cnxt_expired(weak_handle);
}
