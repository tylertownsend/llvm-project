// RUN: %clang_cc1 -x cnxt -std=cnxt1 -E %s | FileCheck %s
// RUN: %clang_cc1 -x cnxt -std=cnxt1 -nostdinc++ -fsyntax-only %s

// CHECK: # 1 "<cnxt-prelude>" 3
// CHECK-NOT: <memory>
// CHECK-NOT: std::unique_ptr
// CHECK-NOT: std::shared_ptr
// CHECK-NOT: std::weak_ptr
// CHECK: template <typename T> struct unique {
// CHECK: template <typename T> struct shared {
// CHECK: template <typename T> struct weak {

unique<int> U;
shared<int> S;
weak<int> W;

int sentinel;
