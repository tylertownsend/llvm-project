// RUN: %clang_cc1 -x cnxt -std=cnxt1 -E %s | FileCheck %s

// CHECK: # 1 "<cnxt-prelude>" 3
// CHECK: template <typename T> using unique = std::unique_ptr<T>;
// CHECK: template <typename T> struct shared {};
// CHECK: template <typename T> struct weak {};

int sentinel;
