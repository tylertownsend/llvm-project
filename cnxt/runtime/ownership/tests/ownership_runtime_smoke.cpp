#include "cnxt/runtime/ownership.h"

#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <new>

namespace {

struct Payload {
  uint64_t Value;
};

int DestructionCount = 0;

void destroyPayload(void *Object) {
  if (!Object)
    return;

  ++DestructionCount;
  static_cast<Payload *>(Object)->~Payload();
}

Payload *makePayload(uint64_t Value) {
  void *Storage = __cnxt_rt_own_v1_alloc(sizeof(Payload), alignof(Payload));
  return new (Storage) Payload{Value};
}

int runCleanLifecycle() {
  DestructionCount = 0;

  void *Control = __cnxt_rt_own_v1_shared_from_unique(
      makePayload(7), destroyPayload, sizeof(Payload), alignof(Payload));
  if (!Control)
    return EXIT_FAILURE;

  __cnxt_rt_own_v1_shared_retain(Control);
  __cnxt_rt_own_v1_weak_retain(Control);

  if (__cnxt_rt_own_v1_weak_expired(Control) != 0)
    return EXIT_FAILURE;

  void *Locked = __cnxt_rt_own_v1_weak_lock(Control);
  if (Locked != Control)
    return EXIT_FAILURE;

  auto *Value = static_cast<Payload *>(__cnxt_rt_own_v1_shared_get(Locked));
  if (!Value || Value->Value != 7)
    return EXIT_FAILURE;

  __cnxt_rt_own_v1_shared_release(Locked);
  __cnxt_rt_own_v1_shared_release(Control);
  __cnxt_rt_own_v1_shared_release(Control);

  if (DestructionCount != 1)
    return EXIT_FAILURE;
  if (__cnxt_rt_own_v1_weak_expired(Control) != 1)
    return EXIT_FAILURE;
  if (__cnxt_rt_own_v1_weak_lock(Control) != nullptr)
    return EXIT_FAILURE;

  __cnxt_rt_own_v1_weak_release(Control);

  void *UniqueObject = makePayload(11);
  __cnxt_rt_own_v1_unique_drop(UniqueObject, destroyPayload, sizeof(Payload),
                               alignof(Payload));

  return DestructionCount == 2 ? EXIT_SUCCESS : EXIT_FAILURE;
}

int runLeak() {
  (void)__cnxt_rt_own_v1_shared_from_unique(
      makePayload(99), destroyPayload, sizeof(Payload), alignof(Payload));
  return EXIT_SUCCESS;
}

int runDoubleFree() {
  void *Object = __cnxt_rt_own_v1_alloc(sizeof(Payload), alignof(Payload));
  __cnxt_rt_own_v1_unique_drop(Object, nullptr, sizeof(Payload),
                               alignof(Payload));
  __cnxt_rt_own_v1_unique_drop(Object, nullptr, sizeof(Payload),
                               alignof(Payload));
  return EXIT_SUCCESS;
}

} // namespace

int main(int argc, char **argv) {
  if (argc != 2)
    return EXIT_FAILURE;

  if (std::strcmp(argv[1], "clean") == 0)
    return runCleanLifecycle();
  if (std::strcmp(argv[1], "leak") == 0)
    return runLeak();
  if (std::strcmp(argv[1], "double_free") == 0)
    return runDoubleFree();

  return EXIT_FAILURE;
}
