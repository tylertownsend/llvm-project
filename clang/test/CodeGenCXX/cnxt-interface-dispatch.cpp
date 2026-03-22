// RUN: %clang_cc1 -triple x86_64-unknown-linux-gnu -x cnxt -std=cnxt1 -emit-llvm -o - %s | FileCheck %s

interface CounterLike {
  int next();
  void reset();
};

interface Resettable {
  void reset();
};

class Counter implements CounterLike, Resettable {
public:
  int next();
  void reset();
};

int call_next(CounterLike view) {
  return view.next();
}

void call_counter_reset(CounterLike view) {
  view.reset();
}

void call_iface_reset(Resettable view) {
  view.reset();
}

// CHECK-LABEL: define{{.*}}i32 @_Z9call_next
// CHECK: %[[OBJ_SLOT:.*]] = getelementptr inbounds {{.*}}, ptr %[[VIEW_ADDR:.*]], i32 0, i32 0
// CHECK: store ptr %{{.*}}, ptr %[[OBJ_SLOT]], align
// CHECK: %[[IFACE_PTR:.*]] = call noundef ptr @_ZNK21__cnxt_iface_borrowedI11CounterLikeE8__objectEv
// CHECK: %[[VTABLE:.*]] = load ptr, ptr %[[IFACE_PTR]], align
// CHECK: %[[SLOT:.*]] = getelementptr inbounds ptr, ptr %[[VTABLE]], i64 0
// CHECK: %[[FN:.*]] = load ptr, ptr %[[SLOT]], align
// CHECK: %[[RESULT:.*]] = call noundef i32 %[[FN]](ptr noundef nonnull align 8 dereferenceable(8) %[[IFACE_PTR]])
// CHECK: ret i32 %[[RESULT]]

// CHECK-LABEL: define{{.*}}void @_Z18call_counter_reset
// CHECK: %[[COUNTER_OBJ:.*]] = call noundef ptr @_ZNK21__cnxt_iface_borrowedI11CounterLikeE8__objectEv
// CHECK: %[[COUNTER_VTABLE:.*]] = load ptr, ptr %[[COUNTER_OBJ]], align
// CHECK: %[[COUNTER_SLOT:.*]] = getelementptr inbounds ptr, ptr %[[COUNTER_VTABLE]], i64 1
// CHECK: %[[COUNTER_FN:.*]] = load ptr, ptr %[[COUNTER_SLOT]], align
// CHECK: call void %[[COUNTER_FN]](ptr noundef nonnull align 8 dereferenceable(8) %[[COUNTER_OBJ]])
// CHECK: ret void

// CHECK-LABEL: define{{.*}}void @_Z16call_iface_reset
// CHECK: %[[RESETTABLE_OBJ:.*]] = call noundef ptr @_ZNK21__cnxt_iface_borrowedI10ResettableE8__objectEv
// CHECK: %[[RESETTABLE_VTABLE:.*]] = load ptr, ptr %[[RESETTABLE_OBJ]], align
// CHECK: %[[RESETTABLE_SLOT:.*]] = getelementptr inbounds ptr, ptr %[[RESETTABLE_VTABLE]], i64 0
// CHECK: %[[RESETTABLE_FN:.*]] = load ptr, ptr %[[RESETTABLE_SLOT]], align
// CHECK: call void %[[RESETTABLE_FN]](ptr noundef nonnull align 8 dereferenceable(8) %[[RESETTABLE_OBJ]])
// CHECK: ret void
