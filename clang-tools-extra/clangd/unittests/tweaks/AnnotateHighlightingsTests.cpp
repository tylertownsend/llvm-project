//===-- AnnotateHighlightingsTests.cpp --------------------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "TweakTesting.h"
#include "gtest/gtest.h"

namespace clang {
namespace clangd {
namespace {

TWEAK_TEST(AnnotateHighlightings);

TEST_F(AnnotateHighlightingsTest, Test) {
  EXPECT_AVAILABLE("^vo^id^ ^f(^) {^}^"); // available everywhere.
  EXPECT_AVAILABLE("[[int a; int b;]]");
  EXPECT_EQ("void /* Function [decl] [def] [globalScope] */f() {}",
            apply("void ^f() {}"));

  EXPECT_EQ(apply("[[int f1(); const int x = f1();]]"),
            "int /* Function [decl] [globalScope] */f1(); "
            "const int /* Variable [decl] [def] [readonly] [fileScope] */x = "
            "/* Function [globalScope] */f1();");

  // Only the targeted range is annotated.
  EXPECT_EQ(apply("void f1(); void f2() {^}"),
            "void f1(); "
            "void /* Function [decl] [def] [globalScope] */f2() {}");
}

TEST_F(AnnotateHighlightingsTest, CNxtRestrictedConstructsUnavailable) {
  FileName = "TestTU.cn";
  ExtraArgs = {"-x", "cnxt", "-std=cnxt1"};
  Context = Function;

  EXPECT_AVAILABLE("^int value = 0;");
  EXPECT_UNAVAILABLE("^goto done; done:;");
  EXPECT_UNAVAILABLE("^new int;");
  EXPECT_UNAVAILABLE("^throw 1;");
  EXPECT_UNAVAILABLE("^try {} catch (...) {}");
  EXPECT_UNAVAILABLE("^for(int i = 0; i < 2; ++i) {}");
}

TEST_F(AnnotateHighlightingsTest, CNxtRestrictedFilePatternsUnavailable) {
  FileName = "TestTU.cn";
  ExtraArgs = {"-x", "cnxt", "-std=cnxt1"};

  EXPECT_UNAVAILABLE("^template <typename T> struct Box {};");
  EXPECT_UNAVAILABLE("^#include \"dep.cn\"");
}

} // namespace
} // namespace clangd
} // namespace clang
