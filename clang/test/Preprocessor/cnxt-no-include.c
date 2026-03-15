// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

#include "header.h" // expected-error {{cNxt does not support textual include directives; use module imports}}
