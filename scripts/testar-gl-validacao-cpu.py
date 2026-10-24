#!/usr/bin/env python3
"""Exercita o wrapper de produção com validação/WP simulados, sem kernel/GPU."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/gl-validacao-cpu'


def main():
    (OUT / 'Headers').mkdir(parents=True, exist_ok=True)
    for name in ('kern_mach.hpp', 'kern_patcher.hpp'):
        (OUT / 'Headers' / name).write_text('// Stubs declarados explicitamente no harness.\n')
    source = r'''
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include <vector>
using UInt8=uint8_t; using UInt32=uint32_t;
using mach_vm_address_t=uintptr_t; using memory_object_t=void*; using memory_object_offset_t=unsigned long long;
constexpr int KERN_SUCCESS=0;
static bool failEnable=false,failRestore=false,race=false,locked=false;
static unsigned copies=0,originalCalls=0;
static std::vector<int> sequence;
static std::array<unsigned char,4096> page;
struct KernelPatcher {
 static inline void* kernelWriteLock=nullptr;
 static constexpr unsigned KernelID=0;
 struct RouteRequest {template<class T> RouteRequest(const char*,T,mach_vm_address_t&) {}};
 bool routeMultipleLong(unsigned,RouteRequest*,unsigned){return true;}
 void clearError(){}
};
struct NRed {
 std::map<std::string,unsigned> props;
 static NRed& singleton(){static NRed n;return n;}
 unsigned getDeviceID(){return 0x164c;}
 void setProp32(const char* k,unsigned v){assert(!locked);props[k]=v;}
};
struct Version {unsigned major(){return 25;}unsigned minor(){return 6;}};
Version currentKernelVersion(){return {};}
struct MachInfo { static int setKernelWriting(bool enable,void*) {
 sequence.push_back(enable?1:0);
 if(enable&&failEnable)return 1;
 locked=enable;
 if(enable&&race)page[0]^=1;
 return !enable&&failRestore?1:0;
}};
void lilu_os_memcpy(void* dst,const void* src,size_t n){assert(locked);assert(n==6);assert(dst==page.data()+0x1b9);copies++;memcpy(dst,src,n);}
#include <UserGLBlend.hpp>
static int validOut=15,taintOut=0,nxOut=0;
void original(void* vp,memory_object_t pager,memory_object_offset_t off,const void* data,int* validated,int* tainted,int* nx){
 assert(!locked);assert(vp==(void*)1&&pager==(void*)2);assert(off==0x8000||off==0x9000);
 assert(data==page.data());originalCalls++;
 *validated=validOut;*tainted=taintOut;*nx=nxOut;
}
void reset(){
 memcpy(page.data(),UserGLBlendData::OriginalPage,page.size());
 failEnable=failRestore=race=locked=false;copies=originalCalls=0;sequence.clear();
 validOut=15;taintOut=nxOut=0;
 UserGLBlend::appliedPages=UserGLBlend::writeFailures=UserGLBlend::restoreFailures=0;
 UserGLBlend::originalValidatePage=(uintptr_t)&original;
}
void run(unsigned long long offset=0x8000){
 int v=-1,t=-1,n=-1;
 UserGLBlend::wrappedValidatePage((void*)1,(void*)2,offset,page.data(),&v,&t,&n);
 assert(originalCalls==1);assert(v==validOut&&t==taintOut&&n==nxOut);assert(!locked);
}
int main(){
 reset();run();assert(copies==1&&UserGLBlend::appliedPages==1);assert((sequence==std::vector<int>{1,0}));
 auto expected=page;memcpy(expected.data(),UserGLBlendData::OriginalPage,4096);
 memcpy(expected.data()+0x1b9,UserGLBlendData::Replacement,6);assert(page==expected);
 // Página já modificada: não escreve nem conta novamente.
 originalCalls=0;run();assert(copies==1&&UserGLBlend::appliedPages==1);
 for(unsigned mode=0;mode<7;mode++){
  reset();
  if(mode==0)validOut=0;if(mode==1)validOut=1;if(mode==2)taintOut=15;
  if(mode==3)nxOut=15;if(mode==4)page[4095]^=1;if(mode==5)page[0x1b9]^=1;
  auto before=page;run(mode==6?0x9000:0x8000);
  assert(page==before&&copies==0&&sequence.empty()&&UserGLBlend::appliedPages==0);
 }
 reset();failEnable=true;auto before=page;run();assert(page==before&&copies==0&&UserGLBlend::writeFailures==1);assert((sequence==std::vector<int>{1}));
 reset();failRestore=true;run();assert(copies==1&&UserGLBlend::restoreFailures==1&&UserGLBlend::appliedPages==0);assert((sequence==std::vector<int>{1,0}));
 reset();race=true;run();assert(copies==0&&UserGLBlend::appliedPages==0);assert((sequence==std::vector<int>{1,0}));
 // Entradas incompletas nunca chegam ao writer.
 auto writer=[](void*){assert(false);return UserGLBlendCore::Outcome::Applied;};
 int v=15,t=0,n=0;
 assert(UserGLBlendCore::afterValidation(nullptr,0x8000,&v,&t,&n,writer)==UserGLBlendCore::Outcome::Unchanged);
 assert(UserGLBlendCore::afterValidation(page.data(),0x8000,nullptr,&t,&n,writer)==UserGLBlendCore::Outcome::Unchanged);
 assert(UserGLBlendCore::afterValidation(page.data(),0x8000,&v,nullptr,&n,writer)==UserGLBlendCore::Outcome::Unchanged);
 assert(UserGLBlendCore::afterValidation(page.data(),0x8000,&v,&t,nullptr,writer)==UserGLBlendCore::Outcome::Unchanged);
 KernelPatcher patcher;UserGLBlend::init(patcher);UserGLBlend::publishCounters();
 assert(NRed::singleton().props["NRedGLBlendEnabled"]==1);
 puts("PASS production page wrapper: 7 args forwarded, native outputs preserved, full-page/offset/validation gates, exact 6-byte write, idempotency, WP failure/restore failure/concurrent change; no kernel or GPU execution");
}
'''
    path, exe = OUT / 'test.cpp', OUT / 'test'
    path.write_text(source)
    subprocess.run(['/usr/bin/clang++', '-std=c++23', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-I', str(OUT), '-I', str(ROOT / 'source/NootedRed/NootedRed'),
                    str(path), '-o', str(exe)], check=True, timeout=60)
    result = subprocess.run([str(exe)], capture_output=True, text=True, check=True, timeout=30)
    (OUT / 'resultado.txt').write_text(result.stdout)
    print(result.stdout.strip())


if __name__ == '__main__':
    main()
