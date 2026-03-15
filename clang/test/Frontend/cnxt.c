// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only %s
// RUN: not %clang_cc1 -x cnxt -std=c++20 -fsyntax-only %s 2>&1 | FileCheck %s --check-prefix=INVALID-CNXT
// RUN: not %clang_cc1 -x c++ -std=cnxt1 -fsyntax-only %s 2>&1 | FileCheck %s --check-prefix=INVALID-CXX

// INVALID-CNXT: error: invalid argument '-std=c++20' not allowed with 'cNxt'
// INVALID-CXX: error: invalid argument '-std=cnxt1' not allowed with 'C++'

int identity(int value) { return value; }
