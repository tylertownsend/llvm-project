#include "cnxt/runtime/ownership.h"

#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <new>

namespace {

struct ControlBlock {
  std::atomic<uint64_t> Strong{1};
  std::atomic<uint64_t> Weak{1};
  void *Object = nullptr;
  void (*Destructor)(void *) = nullptr;
  uint64_t Size = 0;
  uint64_t Align = 0;
};

[[noreturn]] void oomAbort() { std::abort(); }

uint64_t normalizeSize(uint64_t Size) { return Size == 0 ? 1 : Size; }

uint64_t normalizeAlign(uint64_t Align) {
  uint64_t DefaultAlign = alignof(std::max_align_t);
  if (Align == 0)
    return DefaultAlign;
  if ((Align & (Align - 1)) != 0)
    return DefaultAlign;
  if (Align < alignof(void *))
    return alignof(void *);
  return Align;
}

void dropPayload(ControlBlock *CB) {
  void *Object = CB->Object;
  if (!Object)
    return;

  CB->Object = nullptr;
  if (CB->Destructor)
    CB->Destructor(Object);

  ::operator delete(Object,
                    std::align_val_t(static_cast<std::size_t>(
                        normalizeAlign(CB->Align))));
}

} // namespace

extern "C" uint32_t __cnxt_rt_own_v1_abi_version(void) { return 1; }

extern "C" void *__cnxt_rt_own_v1_alloc(uint64_t Size, uint64_t Align) {
  Size = normalizeSize(Size);
  Align = normalizeAlign(Align);
  void *Object = ::operator new(static_cast<std::size_t>(Size),
                                std::align_val_t(static_cast<std::size_t>(Align)),
                                std::nothrow);
  if (!Object)
    oomAbort();
  return Object;
}

extern "C" void __cnxt_rt_own_v1_unique_drop(void *Object, void (*Dtor)(void *),
                                              uint64_t Size, uint64_t Align) {
  if (!Object)
    return;

  (void)Size;
  Align = normalizeAlign(Align);
  if (Dtor)
    Dtor(Object);
  ::operator delete(Object,
                    std::align_val_t(static_cast<std::size_t>(Align)));
}

extern "C" void *
__cnxt_rt_own_v1_shared_from_unique(void *Object, void (*Dtor)(void *),
                                    uint64_t Size, uint64_t Align) {
  if (!Object)
    return nullptr;

  auto *CB = new (std::nothrow) ControlBlock();
  if (!CB)
    oomAbort();

  CB->Object = Object;
  CB->Destructor = Dtor;
  CB->Size = Size;
  CB->Align = normalizeAlign(Align);
  return CB;
}

extern "C" void __cnxt_rt_own_v1_shared_retain(void *Control) {
  if (!Control)
    return;
  auto *CB = static_cast<ControlBlock *>(Control);
  CB->Strong.fetch_add(1, std::memory_order_relaxed);
}

extern "C" void __cnxt_rt_own_v1_shared_release(void *Control) {
  if (!Control)
    return;

  auto *CB = static_cast<ControlBlock *>(Control);
  if (CB->Strong.fetch_sub(1, std::memory_order_acq_rel) == 1) {
    dropPayload(CB);
    __cnxt_rt_own_v1_weak_release(Control);
  }
}

extern "C" void *__cnxt_rt_own_v1_shared_get(void *Control) {
  if (!Control)
    return nullptr;
  auto *CB = static_cast<ControlBlock *>(Control);
  return CB->Object;
}

extern "C" void __cnxt_rt_own_v1_weak_retain(void *Control) {
  if (!Control)
    return;
  auto *CB = static_cast<ControlBlock *>(Control);
  CB->Weak.fetch_add(1, std::memory_order_relaxed);
}

extern "C" void __cnxt_rt_own_v1_weak_release(void *Control) {
  if (!Control)
    return;

  auto *CB = static_cast<ControlBlock *>(Control);
  if (CB->Weak.fetch_sub(1, std::memory_order_acq_rel) == 1)
    delete CB;
}

extern "C" void *__cnxt_rt_own_v1_weak_lock(void *Control) {
  if (!Control)
    return nullptr;

  auto *CB = static_cast<ControlBlock *>(Control);
  uint64_t Strong = CB->Strong.load(std::memory_order_acquire);
  while (Strong != 0) {
    if (CB->Strong.compare_exchange_weak(Strong, Strong + 1,
                                         std::memory_order_acq_rel,
                                         std::memory_order_acquire)) {
      return Control;
    }
  }
  return nullptr;
}

extern "C" uint8_t __cnxt_rt_own_v1_weak_expired(void *Control) {
  if (!Control)
    return 1;
  auto *CB = static_cast<ControlBlock *>(Control);
  return CB->Strong.load(std::memory_order_acquire) == 0 ? 1 : 0;
}
