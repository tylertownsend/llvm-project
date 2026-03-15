// RUN: %clang_cc1 -x cnxt -std=cnxt1 -E %s | FileCheck %s

// CHECK: # 1 "<cnxt-prelude>" 3
// CHECK-NEXT: template <typename T> struct unique {};
// CHECK-NEXT: template <typename T> struct shared {};
// CHECK-NEXT: template <typename T> struct weak {};

int sentinel;
