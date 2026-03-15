// RUN: not %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only %s 2>&1 | FileCheck %s

template <typename T>
struct Box {
  T value;
};
// CHECK: error: cNxt does not support template declarations

void reject_template_argument_list() {
  Box<int> value;
  (void)value;
}
// CHECK: error: cNxt does not support template argument lists
