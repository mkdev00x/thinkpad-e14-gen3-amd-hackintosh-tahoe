// Consulta APIs públicas. Não cria comandos Metal nem decodifica frames.
#import <Metal/Metal.h>
#import <VideoToolbox/VideoToolbox.h>
#include <cstdio>

int main() {
    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        printf("metal_device_present=%s\n", device ? "true" : "false");
        if (device) {
            printf("metal_device_name=%s\n", device.name.UTF8String);
            printf("metal_unified_memory=%s\n", device.hasUnifiedMemory ? "true" : "false");
            printf("metal_mac2_family=%s\n", [device supportsFamily:MTLGPUFamilyMac2] ? "true" : "false");
        }
        const struct { const char* name; CMVideoCodecType type; } codecs[] = {
            {"H264", kCMVideoCodecType_H264}, {"HEVC", kCMVideoCodecType_HEVC},
            {"VP9", kCMVideoCodecType_VP9}, {"AV1", kCMVideoCodecType_AV1}
        };
        for (const auto& codec : codecs)
            printf("hardware_decode_%s=%s\n", codec.name, VTIsHardwareDecodeSupported(codec.type) ? "true" : "false");
        puts("gpu_commands_submitted=false decoded_frames=0");
        return device ? 0 : 1;
    }
}
