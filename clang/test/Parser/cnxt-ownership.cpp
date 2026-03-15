// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s

void accepts_ownership_handles() {
  unique<int> u;
  shared<int> s;
  weak<int> w;
  (void)u;
  (void)s;
  (void)w;
}

void reject_non_handle_template_ids() {
  vector<int> value; // expected-error {{cNxt does not support template argument lists}}
}

template <typename T> // expected-error {{cNxt does not support template declarations}}
struct Box {};
