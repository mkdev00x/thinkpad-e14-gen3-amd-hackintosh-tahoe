// Incluído apenas em UserSurfaceSync.cpp; não cria unidade/estado duplicado.
#pragma once
#include <Headers/kern_mach.hpp>
#include <Headers/kern_patcher.hpp>
#include <UserGLBlendCore.hpp>

namespace UserGLBlend {
// ABI Darwin 25 confirmada no kernel local: void, três ponteiros de saída.
using ValidatePage = void (*)(void*, memory_object_t, memory_object_offset_t,
                             const void*, int*, int*, int*);
mach_vm_address_t originalValidatePage{0};
UInt32 appliedPages{0}, writeFailures{0}, restoreFailures{0};

UserGLBlendCore::Outcome writePage(void* page) {
    using UserGLBlendCore::Outcome;
    if (MachInfo::setKernelWriting(true, KernelPatcher::kernelWriteLock) != KERN_SUCCESS)
        return Outcome::WriteFailure;
    // Revalida sob a trava de escrita; outra validação pode ter tocado a página.
    bool applied = memcmp(page, UserGLBlendData::OriginalPage, sizeof(UserGLBlendData::OriginalPage)) == 0;
    if (applied) lilu_os_memcpy(static_cast<UInt8*>(page) + UserGLBlendData::PatchOffset,
                              UserGLBlendData::Replacement, sizeof(UserGLBlendData::Replacement));
    if (MachInfo::setKernelWriting(false, KernelPatcher::kernelWriteLock) != KERN_SUCCESS)
        return Outcome::RestoreFailure;
    return applied ? Outcome::Applied : Outcome::Unchanged;
}

__attribute__((noinline))
void wrappedValidatePage(void* vnode, memory_object_t pager, memory_object_offset_t offset,
                         const void* data, int* validated, int* tainted, int* nx) {
    reinterpret_cast<ValidatePage>(originalValidatePage)(vnode, pager, offset, data, validated, tainted, nx);
    const auto outcome = UserGLBlendCore::afterValidation(data, offset, validated, tainted, nx, writePage);
    // Sem logs, alocações ou IORegistry no contexto de validação/VM.
    if (outcome == UserGLBlendCore::Outcome::Applied) __atomic_fetch_add(&appliedPages, 1U, __ATOMIC_RELAXED);
    if (outcome == UserGLBlendCore::Outcome::WriteFailure) __atomic_fetch_add(&writeFailures, 1U, __ATOMIC_RELAXED);
    if (outcome == UserGLBlendCore::Outcome::RestoreFailure) __atomic_fetch_add(&restoreFailures, 1U, __ATOMIC_RELAXED);
}

void publishCounters() {
    // Chamado no retorno da syscall de shared-region, fora do callback de VM.
    NRed::singleton().setProp32("NRedGLBlendAppliedPages", __atomic_load_n(&appliedPages, __ATOMIC_RELAXED));
    NRed::singleton().setProp32("NRedGLBlendWriteFailures", __atomic_load_n(&writeFailures, __ATOMIC_RELAXED));
    NRed::singleton().setProp32("NRedGLBlendRestoreFailures", __atomic_load_n(&restoreFailures, __ATOMIC_RELAXED));
}

void init(KernelPatcher& patcher) {
    NRed::singleton().setProp32("NRedGLBlendRevision", 1);
    // Perfil local: somente Lucienne 164C/Darwin 25.6; gate DisplayFix no chamador.
    if (NRed::singleton().getDeviceID() != 0x164c || currentKernelVersion().major() != 25 ||
        currentKernelVersion().minor() != 6) {
        NRed::singleton().setProp32("NRedGLBlendRejected", 1);
        return;
    }
    KernelPatcher::RouteRequest request{"_cs_validate_page", wrappedValidatePage, originalValidatePage};
    if (!patcher.routeMultipleLong(KernelPatcher::KernelID, &request, 1)) {
        patcher.clearError();
        NRed::singleton().setProp32("NRedGLBlendRejected", 2);
        return;
    }
    NRed::singleton().setProp32("NRedGLBlendEnabled", 1);
    publishCounters();
}
} // namespace UserGLBlend
