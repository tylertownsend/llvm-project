//===-- ClangCNxtFuzzer.cpp - Fuzz cNxt parser/sema -----------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//
///
/// \file
/// This file implements a fuzzer entrypoint that feeds raw text into Clang's
/// cNxt parser and semantic analysis paths.
///
//===----------------------------------------------------------------------===//

#include "handle-cxx/handle_cxx.h"

using namespace clang_fuzzer;

extern "C" int LLVMFuzzerInitialize(int *argc, char ***argv) { return 0; }

extern "C" int LLVMFuzzerTestOneInput(uint8_t *data, size_t size) {
  std::string S(reinterpret_cast<const char *>(data), size);
  HandleCXXSyntaxOnly(S, "./test.cn", {"-x", "cnxt", "-std=cnxt1"});
  return 0;
}
