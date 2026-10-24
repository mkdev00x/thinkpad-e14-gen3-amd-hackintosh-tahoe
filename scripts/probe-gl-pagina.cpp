// Lê uma página RX do arquivo assinado. Nunca executa código do driver/GL/GPU.
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <mach-o/loader.h>
#include <sys/mman.h>
#include <unistd.h>

int main() {
    const char* path = "/System/Library/Extensions/AMDRadeonX5000GLDriver.bundle/Contents/MacOS/AMDRadeonX5000GLDriver";
    int fd = open(path, O_RDONLY);
    if (fd < 0) { perror("open"); return 1; }
    mach_header_64 header{};
    if (pread(fd, &header, sizeof(header), 0) != sizeof(header) || header.magic != MH_MAGIC_64) return 2;
    off_t cursor = sizeof(header);
    linkedit_data_command signature{};
    for (uint32_t i = 0; i < header.ncmds; ++i) {
        load_command command{};
        if (pread(fd, &command, sizeof(command), cursor) != sizeof(command) || command.cmdsize < sizeof(command)) return 3;
        if (command.cmd == LC_CODE_SIGNATURE && pread(fd, &signature, sizeof(signature), cursor) != sizeof(signature)) return 4;
        cursor += command.cmdsize;
    }
    if (!signature.datasize) return 5;
    fsignatures_t sig{};
    sig.fs_blob_start = reinterpret_cast<void*>(static_cast<uintptr_t>(signature.dataoff));
    sig.fs_blob_size = signature.datasize;
    errno = 0;
    int status = fcntl(fd, F_ADDFILESIGS_RETURN, &sig);
    int sigerrno = errno;
    printf("signature_registration=%d errno=%d (%s)\n", status, sigerrno, strerror(sigerrno));
    auto* page = static_cast<const uint8_t*>(mmap(nullptr, 4096, PROT_READ | PROT_EXEC, MAP_PRIVATE, fd, 0x8000));
    if (page == MAP_FAILED) { perror("mmap"); close(fd); return 6; }
    const uint8_t expected[] = {0xb9, 0x02, 0x00, 0x00, 0x00, 0x90};
    const uint8_t original[] = {0x8b, 0x88, 0xa0, 0x00, 0x00, 0x00};
    uint8_t bytes[6];
    memcpy(bytes, page + 0x1b9, sizeof(bytes));
    printf("mapped_bytes=");
    for (auto b : bytes) printf("%02x", b);
    printf("\npatch_observed=%s original_observed=%s gpu_commands_submitted=false driver_code_executed=false\n",
           memcmp(bytes, expected, 6) == 0 ? "true" : "false", memcmp(bytes, original, 6) == 0 ? "true" : "false");
    munmap(const_cast<uint8_t*>(page), 4096);
    close(fd);
    return memcmp(bytes, expected, 6) == 0 ? 0 : 10;
}
