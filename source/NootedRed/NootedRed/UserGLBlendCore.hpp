// Núcleo testável do patch GL. Preserva a validação nativa de assinatura.
#pragma once
#include <UserGLBlendData.hpp>

namespace UserGLBlendCore {
enum class Outcome : unsigned { Unchanged, Applied, WriteFailure, RestoreFailure };

template<class Writer>
Outcome afterValidation(const void* data, unsigned long long offset,
                        const int* validated, const int* tainted, const int* nx, Writer write) {
    if (data == nullptr || offset != UserGLBlendData::FileOffset ||
        validated == nullptr || tainted == nullptr || nx == nullptr ||
        *validated != 0xf || *tainted != 0 || *nx != 0) return Outcome::Unchanged;
    if (memcmp(data, UserGLBlendData::OriginalPage, sizeof(UserGLBlendData::OriginalPage)) != 0)
        return Outcome::Unchanged;
    return write(const_cast<void*>(data));
}
} // namespace UserGLBlendCore
