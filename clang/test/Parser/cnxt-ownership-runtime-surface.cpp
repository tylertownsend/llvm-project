// RUN: %clang_cc1 -x cnxt -std=cnxt1 -fsyntax-only -verify %s
// expected-no-diagnostics

void parser_runtime_surface(unique<int> strong, shared<int> owner,
                            weak<int> observer) {
  unique<int> moved = static_cast<unique<int> &&>(strong);
  shared<int> widened = share(static_cast<unique<int> &&>(moved));
  shared<int> copied = owner;
  weak<int> aliased(owner);
  shared<int> recovered = observer.lock();
  bool expired = observer.expired();

  moved.reset();
  (void)widened.use_count();
  (void)copied.use_count();
  (void)aliased.expired();
  (void)recovered.use_count();
  (void)expired;

  copied.reset();
  widened.reset();
  recovered.reset();
}
