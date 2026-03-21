#ifndef CNXT_RUNTIME_OWNERSHIP_H
#define CNXT_RUNTIME_OWNERSHIP_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

uint32_t __cnxt_rt_own_v1_abi_version(void);

void *__cnxt_rt_own_v1_alloc(uint64_t size, uint64_t align);
void __cnxt_rt_own_v1_unique_drop(void *object, void (*dtor)(void *),
                                  uint64_t size, uint64_t align);

void *__cnxt_rt_own_v1_shared_from_unique(void *object, void (*dtor)(void *),
                                          uint64_t size, uint64_t align);
void __cnxt_rt_own_v1_shared_retain(void *control);
void __cnxt_rt_own_v1_shared_release(void *control);
void *__cnxt_rt_own_v1_shared_get(void *control);

void __cnxt_rt_own_v1_weak_retain(void *control);
void __cnxt_rt_own_v1_weak_release(void *control);
void *__cnxt_rt_own_v1_weak_lock(void *control);
uint8_t __cnxt_rt_own_v1_weak_expired(void *control);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // CNXT_RUNTIME_OWNERSHIP_H
