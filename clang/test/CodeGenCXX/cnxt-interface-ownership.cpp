// RUN: %clang_cc1 -triple x86_64-unknown-linux-gnu -x cnxt -std=cnxt1 -emit-llvm -o - %s | FileCheck %s

interface CounterLike {
  int next();
};

class Counter implements CounterLike {
public:
  int next();
};

unique<CounterLike> make_iface_owner() {
  return make<Counter>();
}

shared<CounterLike> make_iface_shared() {
  unique<Counter> concrete = make<Counter>();
  return share(static_cast<unique<Counter> &&>(concrete));
}

shared<CounterLike> share_iface_owner(unique<CounterLike> owner) {
  return share(static_cast<unique<CounterLike> &&>(owner));
}

int from_unique(unique<CounterLike> owner) {
  return owner.next();
}

int from_shared(shared<CounterLike> owner) {
  return owner.next();
}

int from_locked(weak<CounterLike> observer) {
  return observer.lock().next();
}

// CHECK-LABEL: define dso_local void @_Z16make_iface_ownerv(
// CHECK: call void @_Z4makeI7CounterJEE6uniqueIT_EDpOT0_(
// CHECK: call void @_ZN6uniqueI11CounterLikeEC1I7CounterPS0_EEOS_IT_E(

// CHECK-LABEL: define dso_local void @_Z17make_iface_sharedv(
// CHECK: call void @_Z5shareI7CounterE6sharedIT_EO6uniqueIS2_E(
// CHECK: call void @_ZN6sharedI11CounterLikeEC1I7CounterPS0_EEOS_IT_E(

// CHECK-LABEL: define dso_local void @_Z17share_iface_owner6uniqueI11CounterLikeE(
// CHECK: call void @_Z5shareI11CounterLikeE6sharedIT_EO6uniqueIS2_E(

// CHECK-LABEL: define linkonce_odr void @_Z5shareI11CounterLikeE6sharedIT_EO6uniqueIS2_E(
// CHECK: call noundef ptr @_ZNK6uniqueI11CounterLikeE6__viewEv(
// CHECK: call noundef ptr @_ZNK6uniqueI11CounterLikeE6__dtorEv(
// CHECK: call noundef i64 @_ZNK6uniqueI11CounterLikeE6__sizeEv(
// CHECK: call noundef i64 @_ZNK6uniqueI11CounterLikeE7__alignEv(
// CHECK: call noundef ptr @_ZN6uniqueI11CounterLikeE17__release_storageEv(
// CHECK: call ptr @__cnxt_rt_own_v1_shared_from_unique(
// CHECK-NOT: @_Z19__cnxt_payload_dtorI11CounterLikeEPFvPvEv

// CHECK-LABEL: define dso_local noundef i32 @_Z11from_unique6uniqueI11CounterLikeE(
// CHECK: call { ptr, ptr } @_ZNK6uniqueI11CounterLikeE10__borrowedEv(
// CHECK: call noundef ptr @_ZNK21__cnxt_iface_borrowedI11CounterLikeE8__objectEv(
// CHECK: %[[VTABLE:.*]] = load ptr, ptr %{{.*}}, align
// CHECK: %[[SLOT:.*]] = getelementptr inbounds ptr, ptr %[[VTABLE]], i64 0
// CHECK: %[[FN:.*]] = load ptr, ptr %[[SLOT]], align
// CHECK: call noundef i32 %[[FN]](ptr noundef nonnull align 8 dereferenceable(8) %{{.*}})

// CHECK-LABEL: define dso_local noundef i32 @_Z11from_shared6sharedI11CounterLikeE(
// CHECK: call { ptr, ptr } @_ZNK6sharedI11CounterLikeE10__borrowedEv(
// CHECK: call noundef ptr @_ZNK21__cnxt_iface_borrowedI11CounterLikeE8__objectEv(

// CHECK-LABEL: define dso_local noundef i32 @_Z11from_locked4weakI11CounterLikeE(
// CHECK: call void @_ZNK4weakI11CounterLikeE4lockEv(
// CHECK: call { ptr, ptr } @_ZNK6sharedI11CounterLikeE10__borrowedEv(
// CHECK: call noundef ptr @_ZNK21__cnxt_iface_borrowedI11CounterLikeE8__objectEv(
