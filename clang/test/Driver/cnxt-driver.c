// RUN: %clang -### -c %S/Inputs/cnxt-test.cn 2>&1 | FileCheck %s --check-prefix=EXT-CN
// RUN: %clang -### -c %S/Inputs/cnxt-test.cnxt 2>&1 | FileCheck %s --check-prefix=EXT-CNXT
// RUN: %clang -### -x cnxt -std=cnxt1 -c %s 2>&1 | FileCheck %s --check-prefix=ARGS

// EXT-CN: "-cc1"
// EXT-CN-SAME: "-x" "cnxt"

// EXT-CNXT: "-cc1"
// EXT-CNXT-SAME: "-x" "cnxt"

// ARGS: "-cc1"
// ARGS-SAME: "-std=cnxt1"
// ARGS-SAME: "-x" "cnxt"

int main(void) { return 0; }
