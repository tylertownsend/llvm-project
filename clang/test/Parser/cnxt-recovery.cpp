// RUN: not %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only %s 2>&1 | FileCheck %s

template <typename T>
struct Temp {
  T value;
};
// CHECK: error: cNxt does not support template declarations

void reject_template_argument_list() {
  Temp<int> value;
  (void)value;
}
// CHECK: error: cNxt does not support template argument lists

struct Base {};
struct Derived : Base {};
// CHECK: error: cNxt does not support inheritance base clauses

struct Ops {
  int operator+(const Ops &) const;
};
// CHECK: error: cNxt does not support operator overloading declarations

int cast_it(double value) {
  return (int)value;
}
// CHECK: error: cNxt does not support C-style casts outside unsafe regions

int still_valid_parsing() {
  int values[2] = {1, 2};
  for (int value : values) {
    if (value == 2)
      return value;
  }
  return 0;
}
