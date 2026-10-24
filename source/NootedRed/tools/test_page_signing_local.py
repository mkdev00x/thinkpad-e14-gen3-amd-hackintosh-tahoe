"""Executa a implementação proposta com falhas de assinatura/permissão simuladas.

Não valida o kernel, não carrega a kext e não submete trabalho à GPU.
"""
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
work = root / 'build/page-signing-local'
work.mkdir(parents=True, exist_ok=True)
header = re.sub(r'^#(?:include|pragma).*\n', '',
                (root / 'NootedRed/UserPatchMemory.hpp').read_text(), flags=re.MULTILINE)
source = r'''
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <map>
#include <string>
#include <vector>
using UInt32=uint32_t; using UInt64=uint64_t;
using vm_map_t=void*; using mach_vm_address_t=uint64_t; using mach_vm_size_t=uint64_t;
using natural_t=unsigned; using mach_msg_type_number_t=unsigned;
using vm_prot_t=int; using kern_return_t=int; using vm_region_recurse_info_t=int*;
struct vm_region_submap_short_info_data_64_t {int protection=0,is_submap=0;};
constexpr unsigned PAGE_SIZE=4096, VM_REGION_SUBMAP_SHORT_INFO_COUNT_64=12;
constexpr int FALSE=0, TRUE=1, KERN_SUCCESS=0, KERN_FAILURE=5;
enum {VM_PROT_NONE=0, VM_PROT_READ=1, VM_PROT_WRITE=2, VM_PROT_EXECUTE=4, VM_PROT_COPY=16};
static std::map<uint64_t,int> protection;
static std::vector<std::string> events;
static unsigned errors=0, signFailures=0, maxFailures=0, rxFailures=0;
static void report(int e) {assert(e!=0); ++errors;}
static int vm_protect(vm_map_t,uint64_t address,unsigned size,int maximum,int flags) {
 assert(size==4096);
 if(maximum) { events.push_back("MAX"); if(maxFailures) {--maxFailures; return 42;} }
 else if(flags==5) { events.push_back("RX"); if(rxFailures) {--rxFailures; return 43;} }
 else events.push_back("RW");
 protection[address]=flags&7; return 0;
}
HEADER
static int sign(vm_map_t,uint64_t start,uint64_t end) {
 assert(end==start+4096 && (start%4096)==0 && protection.at(start)==5);
 events.push_back("SIGN"); if(signFailures) {--signFailures; return 44;} return 0;
}
static void reset() {
 events.clear(); errors=signFailures=maxFailures=rxFailures=0;
 protection={{4096,3},{8192,3}}; UserPatchMemory::signMemory=sign;
}
int main() {
 using namespace UserPatchMemory;
 reset(); Page p{4096,5,true};
 assert(restorePages(nullptr,&p,1,report));
 assert((events==std::vector<std::string>{"RX","SIGN","MAX"}));
 assert(!p.writable&&!p.signaturePending&&!p.maximumPending);
 auto before=events.size(); assert(restorePages(nullptr,&p,1,report)&&events.size()==before);
 // Nenhum hook de assinatura: não declarar conclusão nem fechar a transação.
 reset(); p=Page{4096,5,true}; signMemory=nullptr;
 assert(!restorePages(nullptr,&p,1,report)&&p.signaturePending&&p.maximumPending);
 signMemory=sign; assert(restorePages(nullptr,&p,1,report));
 assert((events==std::vector<std::string>{"RX","SIGN","MAX"}));
 // Falha da assinatura deve ser repetível, sem reabrir para escrita.
 reset(); p=Page{4096,5,true}; signFailures=1;
 assert(!restorePages(nullptr,&p,1,report)&&p.signaturePending&&!p.writable);
 assert(restorePages(nullptr,&p,1,report));
 assert((events==std::vector<std::string>{"RX","SIGN","SIGN","MAX"}));
 // Regravar os bytes originais também exige nova validação da página COW.
 assert(prepareRollback(nullptr,&p,1,4096,8,report));
 assert(restorePages(nullptr,&p,1,report));
 assert((std::vector<std::string>(events.end()-4,events.end())==std::vector<std::string>{"RW","RX","SIGN","MAX"}));
 // Falha de max após assinatura não deve marcar tudo concluído, nem reassinar sem escrita.
 reset(); p=Page{4096,5,true}; maxFailures=1;
 assert(!restorePages(nullptr,&p,1,report)&&p.maximumPending&&!p.signaturePending);
 assert(restorePages(nullptr,&p,1,report));
 assert((events==std::vector<std::string>{"RX","SIGN","MAX","MAX"}));
 // Falha de RX não deve passar à assinatura.
 reset(); p=Page{4096,5,true}; rxFailures=2;
 assert(!restorePages(nullptr,&p,1,report)&&p.writable);
 assert((events==std::vector<std::string>{"RX","RX"}));
 assert(restorePages(nullptr,&p,1,report));
 // Uma página com assinatura pendente não impede restaurar as demais.
 reset(); Page pages[]={{4096,5,true},{8192,5,true}}; signFailures=1;
 assert(!restorePages(nullptr,pages,2,report));
 assert(pages[0].signaturePending&&!pages[1].signaturePending&&protection.at(8192)==5);
 assert(restorePages(nullptr,pages,2,report));
 puts("PASS: ordem RX/assinatura/max, idempotencia, ausencia e falha de assinatura, rollback, falha RX/max e multiplas paginas");
}
'''.replace('HEADER', header)
path, binary = work / 'test.cpp', work / 'test'
path.write_text(source)
subprocess.run(['xcrun', 'clang++', '-std=c++23', '-O2', '-Wall', '-Wextra', '-Werror', str(path), '-o', str(binary)], check=True, timeout=60)
subprocess.run([str(binary)], check=True, timeout=10)
