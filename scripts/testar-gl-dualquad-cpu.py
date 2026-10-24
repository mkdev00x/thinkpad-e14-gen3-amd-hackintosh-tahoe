#!/usr/bin/env python3
"""Executa só o emissor CPU do driver GL com buffers falsos e submissão bloqueada."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DRIVER = Path('/System/Library/Extensions/AMDRadeonX5000GLDriver.bundle/Contents/MacOS/AMDRadeonX5000GLDriver')
OUT = ROOT / 'build/gl-dualquad-cpu'
SHA = 'ce205f063627a4b82ee8ccee04ab7963a3efb8dec488cb3c53ed6c6719434f80'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = DRIVER.read_bytes()
    cached_patch = False
    # O hook pode já ter alterado a página no cache unificado. Reconstruir
    # somente o buffer local, exigindo o SHA original completo após a reversão.
    if hashlib.sha256(data).hexdigest() != SHA and data[0x81b9:0x81bf] == bytes.fromhex('b90200000090'):
        data = data[:0x81b9] + bytes.fromhex('8b88a0000000') + data[0x81bf:]
        cached_patch = True
    assert hashlib.sha256(data).hexdigest() == SHA, 'Driver diferente do analisado.'
    start, end, change = 0x819e, 0x822c, 0x81b9
    code = data[start:end]
    assert code[change-start:change-start+6] == bytes.fromhex('8b88a0000000')
    assert code[0x81f1-start] == 0xe8 and len(code) == 142
    source = r'''
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <sys/mman.h>
CODE
template<class T> static void put(void* p,size_t off,T v){memcpy((uint8_t*)p+off,&v,sizeof(v));}
template<class T> static T get(const void* p,size_t off){T v;memcpy(&v,(const uint8_t*)p+off,sizeof(v));return v;}
int main(int argc,char**){
 auto* codepage=(uint8_t*)mmap(nullptr,4096,3,MAP_PRIVATE|MAP_ANON,-1,0);assert(codepage!=MAP_FAILED);
 memcpy(codepage,original,sizeof(original));memcpy(codepage+512,original,sizeof(original));
 // A chamada que submeteria pacotes à GPU vira UD2 nos DOIS emissores.
 // O caminho normal usa espaço sobrando no buffer e nunca passa por ela.
 for(size_t off:{size_t(0),size_t(512)}){codepage[off+0x53]=0x0f;codepage[off+0x54]=0x0b;}
 const uint8_t replacement[]={0xb9,0x02,0,0,0,0x90};
 memcpy(codepage+512+0x1b,replacement,6);assert(mprotect(codepage,4096,5)==0);
 using Fn=void(*)(void*);auto before=(Fn)codepage,after=(Fn)(codepage+512);
 alignas(16) std::array<uint8_t,0x4000> ctx{};
 alignas(16) std::array<uint8_t,192> hw{};
 alignas(16) std::array<uint8_t,64> packets{};
 uint32_t random=123,cases=0,originalViolations=0;
 for(unsigned caps=0;caps<256;caps++)for(bool dual:{false,true})for(unsigned i=0;i<128;i++){
  random=random*1664525+1013904223;uint32_t control=random;
  for(unsigned variant=0;variant<2;variant++){
   ctx.fill(0x5a);hw.fill(0);packets.fill(0xcc);
   put(hw.data(),0xa0,uint32_t(caps));put(ctx.data(),0x12d8,hw.data());
   put(ctx.data(),0x30ec,uint32_t(dual?4:0));put(ctx.data(),0x1398,control);
   put(ctx.data(),0xd68,packets.data());
   put(ctx.data(),0xd60,packets.data()+(argc>1?12:64));
   auto expected=ctx;auto hwBefore=hw;
   (variant?after:before)(ctx.data());
   uint32_t expectedBit=variant?unsigned(dual):unsigned(dual&&((caps&2)!=0));
   uint32_t expectedControl=(control&~1U)|expectedBit;
   put(expected.data(),0x1398,expectedControl);
   put(expected.data(),0xd68,packets.data()+12);put(expected.data(),0x30f8,packets.data()+12);
   assert(ctx==expected&&hw==hwBefore);
   assert(get<uint32_t>(packets.data(),0)==0xc0016900&&get<uint32_t>(packets.data(),4)==0x202);
   assert(get<uint32_t>(packets.data(),8)==expectedControl);
   for(size_t j=12;j<packets.size();j++)assert(packets[j]==0xcc);
   if(!variant&&dual&&!(caps&2))originalViolations++;
  }
  cases++;
 }
 assert(originalViolations==16384);
 printf("PASS %u native GL emitter cases; %u original dual-source violations; candidate sets bit 0 for dual-source; all other context/packet bytes preserved; no GPU submission\n",cases,originalViolations);
 assert(munmap(codepage,4096)==0);
}
'''.replace('CODE', 'static const uint8_t original[]={' + ','.join(map(str, code)) + '};')
    path, exe = OUT / 'test.cpp', OUT / 'test'
    path.write_text(source)
    subprocess.run(['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror',str(path),'-o',str(exe)],check=True,timeout=60)
    guard = subprocess.run([str(exe),'--guard-test'],capture_output=True,timeout=10)
    assert guard.returncode == -4, 'A guarda de não-submissão não interceptou a chamada.'
    result = subprocess.run([str(exe)],check=True,capture_output=True,text=True,timeout=30)
    (OUT/'resultado.txt').write_text(result.stdout)
    (OUT/'identidade.json').write_text(json.dumps({'driver_sha256':SHA,'cached_patch_normalized_in_local_buffer':cached_patch,'function_rva':hex(start),
        'function_sha256':hashlib.sha256(code).hexdigest(),'patch_rva':hex(change),
        'find':'8b88a0000000','replace':'b90200000090','gpu_calls_blocked_with_ud2':True,
        'guard_returncode':guard.returncode,'hardware_tested':False},indent=2)+'\n')
    print(result.stdout.strip())


if __name__ == '__main__':
    main()
