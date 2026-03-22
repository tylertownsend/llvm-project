// RUN: split-file %s %t
// RUN: %clang_cc1 -x cnxt -std=cnxt1 -Wno-return-type-c-linkage -emit-llvm -o - %t/export.cn | FileCheck %s --check-prefix=EXPORT
// RUN: %clang_cc1 -x cnxt -std=cnxt1 -Wno-return-type-c-linkage -emit-llvm -o - %t/import.cn | FileCheck %s --check-prefix=IMPORT

// EXPORT: %struct.unique = type { ptr, ptr, ptr, i64, i64 }
// EXPORT: %struct.shared = type { ptr, ptr }
// EXPORT: %struct.weak = type { ptr, ptr }
// EXPORT-LABEL: define{{.*}} @export_unique(
// EXPORT: call {{.*}} @_ZN6uniqueIiEC1EOS0_
// EXPORT-LABEL: define{{.*}} @export_shared(
// EXPORT: call {{.*}} @_ZN6sharedIiEC1EOS0_
// EXPORT-LABEL: define{{.*}} @export_weak(
// EXPORT: call {{.*}} @_ZN4weakIiEC1EOS0_
// EXPORT-LABEL: define{{.*}} @export_lock(
// EXPORT: call {{.*}} @_ZNK4weakIiE4lockEv
// EXPORT-LABEL: define linkonce_odr{{.*}} @_ZNK4weakIiE4lockEv(
// EXPORT: call ptr @__cnxt_rt_own_v1_weak_lock(ptr

// IMPORT: %struct.unique = type { ptr, ptr, ptr, i64, i64 }
// IMPORT: %struct.shared = type { ptr, ptr }
// IMPORT: %struct.weak = type { ptr, ptr }
// IMPORT-LABEL: define{{.*}} @_Z18call_import_unique6uniqueIiE(
// IMPORT: call {{.*}} @_ZN6uniqueIiEC1EOS0_
// IMPORT: call void @import_unique(
// IMPORT: call void @_ZN6uniqueIiED1Ev(
// IMPORT-LABEL: define{{.*}} @_Z18call_import_shared6sharedIiE(
// IMPORT: call {{.*}} @_ZN6sharedIiEC1ERKS0_
// IMPORT: call void @import_shared(
// IMPORT: call void @_ZN6sharedIiED1Ev(
// IMPORT-LABEL: define{{.*}} @_Z16call_import_weak4weakIiE(
// IMPORT: call {{.*}} @_ZN4weakIiEC1ERKS0_
// IMPORT: call void @import_weak(
// IMPORT: call void @_ZN4weakIiED1Ev(
// IMPORT-LABEL: define{{.*}} @_Z16call_import_lock4weakIiE(
// IMPORT: call void @import_lock(

//--- export.cn
cnxt_export_c unique<int> export_unique(unique<int> handle) { return handle; }

cnxt_export_c shared<int> export_shared(shared<int> handle) { return handle; }

cnxt_export_c weak<int> export_weak(weak<int> handle) { return handle; }

cnxt_export_c shared<int> export_lock(weak<int> handle) {
  return handle.lock();
}

//--- import.cn
cnxt_import_c unique<int> import_unique(unique<int> handle);
cnxt_import_c shared<int> import_shared(shared<int> handle);
cnxt_import_c weak<int> import_weak(weak<int> handle);
cnxt_import_c shared<int> import_lock(weak<int> handle);

unique<int> call_import_unique(unique<int> handle) {
  return import_unique(static_cast<unique<int> &&>(handle));
}

shared<int> call_import_shared(shared<int> handle) {
  return import_shared(handle);
}

weak<int> call_import_weak(weak<int> handle) {
  return import_weak(handle);
}

shared<int> call_import_lock(weak<int> handle) {
  return import_lock(handle);
}
