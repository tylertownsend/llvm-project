// RUN: %clang_cc1 -triple x86_64-unknown-linux-gnu -x cnxt -std=cnxt1 -emit-llvm -o - %s | FileCheck %s

interface CounterLike {
  int next();
};

class Counter implements CounterLike {
public:
  int next();
};

int call_next(CounterLike view) {
  return view.next();
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
