#include "cnxt/runtime/ownership.h"

#include <atomic>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <new>
#include <thread>
#include <vector>

namespace {

struct Payload {
  uint64_t Value;
};

std::atomic<int> DestructionCount{0};
volatile uint64_t FreedValueRead = 0;

void destroyPayload(void *Object) {
  if (!Object)
    return;

  DestructionCount.fetch_add(1, std::memory_order_relaxed);
  static_cast<Payload *>(Object)->~Payload();
}

Payload *makePayload(uint64_t Value) {
  void *Storage = __cnxt_rt_own_v1_alloc(sizeof(Payload), alignof(Payload));
  return new (Storage) Payload{Value};
}

int runCleanLifecycle() {
  DestructionCount.store(0, std::memory_order_relaxed);

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

  if (DestructionCount.load(std::memory_order_relaxed) != 1)
    return EXIT_FAILURE;
  if (__cnxt_rt_own_v1_weak_expired(Control) != 1)
    return EXIT_FAILURE;
  if (__cnxt_rt_own_v1_weak_lock(Control) != nullptr)
    return EXIT_FAILURE;

  __cnxt_rt_own_v1_weak_release(Control);

  void *UniqueObject = makePayload(11);
  __cnxt_rt_own_v1_unique_drop(UniqueObject, destroyPayload, sizeof(Payload),
                               alignof(Payload));

  return DestructionCount.load(std::memory_order_relaxed) == 2 ? EXIT_SUCCESS
                                                               : EXIT_FAILURE;
}

int runLeak() {
  (void)__cnxt_rt_own_v1_shared_from_unique(
      makePayload(99), destroyPayload, sizeof(Payload), alignof(Payload));
  return EXIT_SUCCESS;
}

int runUseAfterFree() {
  DestructionCount.store(0, std::memory_order_relaxed);

  void *Control = __cnxt_rt_own_v1_shared_from_unique(
      makePayload(17), destroyPayload, sizeof(Payload), alignof(Payload));
  if (!Control)
    return EXIT_FAILURE;

  auto *Value = static_cast<Payload *>(__cnxt_rt_own_v1_shared_get(Control));
  if (!Value)
    return EXIT_FAILURE;

  __cnxt_rt_own_v1_shared_release(Control);

  FreedValueRead = Value->Value;
  return FreedValueRead == 17 ? EXIT_SUCCESS : EXIT_FAILURE;
}

int runDoubleFree() {
  void *Object = __cnxt_rt_own_v1_alloc(sizeof(Payload), alignof(Payload));
  __cnxt_rt_own_v1_unique_drop(Object, nullptr, sizeof(Payload),
                               alignof(Payload));
  __cnxt_rt_own_v1_unique_drop(Object, nullptr, sizeof(Payload),
                               alignof(Payload));
  return EXIT_SUCCESS;
}

int runWeakLockStress() {
  DestructionCount.store(0, std::memory_order_relaxed);

  void *Control = __cnxt_rt_own_v1_shared_from_unique(
      makePayload(23), destroyPayload, sizeof(Payload), alignof(Payload));
  if (!Control)
    return EXIT_FAILURE;

  __cnxt_rt_own_v1_weak_retain(Control);

  constexpr int WorkerCount = 4;
  constexpr int Iterations = 20000;
  std::atomic<bool> Start{false};
  std::atomic<bool> DroppedStrong{false};
  std::atomic<int> SuccessfulLocks{0};
  std::atomic<int> ExpiredLocks{0};
  std::atomic<int> Failures{0};
  std::vector<std::thread> Workers;
  Workers.reserve(WorkerCount);

  for (int Worker = 0; Worker != WorkerCount; ++Worker) {
    Workers.emplace_back([&] {
      while (!Start.load(std::memory_order_acquire))
        std::this_thread::yield();

      for (int I = 0; I != Iterations; ++I) {
        void *Locked = __cnxt_rt_own_v1_weak_lock(Control);
        if (!Locked) {
          if (DroppedStrong.load(std::memory_order_acquire))
            ExpiredLocks.fetch_add(1, std::memory_order_relaxed);
          continue;
        }

        auto *Value = static_cast<Payload *>(__cnxt_rt_own_v1_shared_get(Locked));
        if (!Value || Value->Value != 23)
          Failures.fetch_add(1, std::memory_order_relaxed);

        SuccessfulLocks.fetch_add(1, std::memory_order_relaxed);
        __cnxt_rt_own_v1_shared_release(Locked);
      }
    });
  }

  Start.store(true, std::memory_order_release);

  int SpinBudget = 100000;
  while (SuccessfulLocks.load(std::memory_order_acquire) < WorkerCount * 8 &&
         SpinBudget-- > 0)
    std::this_thread::yield();

  if (SuccessfulLocks.load(std::memory_order_acquire) < WorkerCount * 8) {
    for (auto &Worker : Workers)
      Worker.join();
    __cnxt_rt_own_v1_shared_release(Control);
    __cnxt_rt_own_v1_weak_release(Control);
    return EXIT_FAILURE;
  }

  DroppedStrong.store(true, std::memory_order_release);
  __cnxt_rt_own_v1_shared_release(Control);

  for (auto &Worker : Workers)
    Worker.join();

  if (Failures.load(std::memory_order_relaxed) != 0)
    return EXIT_FAILURE;
  if (ExpiredLocks.load(std::memory_order_relaxed) == 0)
    return EXIT_FAILURE;
  if (DestructionCount.load(std::memory_order_relaxed) != 1)
    return EXIT_FAILURE;
  if (__cnxt_rt_own_v1_weak_expired(Control) != 1)
    return EXIT_FAILURE;
  if (__cnxt_rt_own_v1_weak_lock(Control) != nullptr)
    return EXIT_FAILURE;

  __cnxt_rt_own_v1_weak_release(Control);
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
  if (std::strcmp(argv[1], "use_after_free") == 0)
    return runUseAfterFree();
  if (std::strcmp(argv[1], "double_free") == 0)
    return runDoubleFree();
  if (std::strcmp(argv[1], "weak_lock_stress") == 0)
    return runWeakLockStress();

  return EXIT_FAILURE;
}
