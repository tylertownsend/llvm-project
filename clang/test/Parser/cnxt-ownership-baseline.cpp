// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only %s

unique<int> pass_unique(unique<int> handle) { return handle; }

shared<int> pass_shared(shared<int> handle) { return handle; }

weak<int> make_weak(shared<int> owner) {
  weak<int> w(owner);
  return w;
}

bool weak_is_expired(weak<int> weak_handle) { return weak_handle.expired(); }

shared<int> weak_lock(weak<int> weak_handle) { return weak_handle.lock(); }
