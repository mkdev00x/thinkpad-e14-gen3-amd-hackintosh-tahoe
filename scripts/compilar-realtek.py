#!/usr/bin/env python3
"""Compila fontes identificadas em área isolada, sem executar Makefile upstream."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'source/RealtekBluetoothFirmware'
COMMIT = '22e501a8a0a7aba8bb4e594bc6f40b1a67391af9'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(source_override=None):
    source = Path(source_override or SOURCE)
    output = ROOT/'build/realtek'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    output.mkdir(parents=True)
    state = {'state':'building_not_installed','source_commit':COMMIT,'output':str(output),'source':str(source),'commands':[]}
    try:
        # Confere que os bytes compactados embutidos são exatamente a imagem
        # RTL8852AU fornecida no mesmo commit. Não envia dados ao dispositivo.
        embedded = (source/'include/FwBinary.cpp').read_text()
        symbol = re.search(r'const unsigned char \*rtl8852au_fw_bin = (\w+);',embedded)[1]
        array = re.search(r'const unsigned char '+symbol+r'\[\] = \{(.*?)\};',embedded,re.S)[1]
        compressed = bytes(int(x,16) for x in re.findall(r'0x([0-9a-fA-F]{2})',array))
        firmware = (source/'fw/rtl8852au_fw.bin').read_bytes()
        assert zlib.decompress(compressed) == firmware
        assert firmware[:8] == b'Realtech' and len(firmware) <= 4*len(compressed)
        state['firmware']={'name':'rtl8852au_fw.bin','size':len(firmware),'sha256':hashlib.sha256(firmware).hexdigest(),
                           'embedded_bytes_verified':True,'device_uploaded':False}
        sdk = Path(subprocess.check_output(['/usr/bin/xcrun','--sdk','macosx','--show-sdk-path'],text=True).strip())
        kernel = sdk/'System/Library/Frameworks/Kernel.framework'
        compiler = '/Library/Developer/CommandLineTools/usr/bin/clang++'
        flags=['-arch','x86_64','-isysroot',str(sdk),'-mmacosx-version-min=12.0','-mno-red-zone',
               '-I'+str(kernel/'Headers'),'-I'+str(kernel/'PrivateHeaders'),
               '-I'+str(source/'include'),'-I'+str(source/'RealtekBluetoothFirmware'),
               '-fno-builtin','-fno-common','-mkernel','-fapple-kext','-fno-exceptions','-fno-rtti',
               '-DKERNEL','-DKERNEL_PRIVATE','-DDRIVER_PRIVATE','-DAPPLE','-DNeXT',
               '-Wno-inconsistent-missing-override','-Wno-unknown-pragmas','-Os']
        inputs=['RealtekBluetoothFirmware/RealtekBluetoothFirmware.cpp','RealtekBluetoothFirmware/BtRtl.cpp',
                'RealtekBluetoothFirmware/USBDeviceController.cpp','include/FwBinary.cpp',
                'RealtekBluetoothFirmware/zutil.c','RealtekBluetoothFirmware/kmod_info.c']
        state['source_hashes']={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()}
        objects=[]
        for name in inputs:
            path=source/name;obj=output/(path.stem+'.o')
            lang=['-x','c'] if name.endswith('kmod_info.c') else ['-std=gnu++14','-x','c++']
            command=[compiler,*flags,*lang,'-c',str(path),'-o',str(obj)]
            state['commands'].append(command)
            print('Compilando:',path.name,flush=True)
            with (output/(path.stem+'.log')).open('wb') as log:
                subprocess.run(command,env=dict(os.environ,CLANG_MODULE_CACHE_PATH=str(output/'module-cache')),
                               stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
            objects.append(obj)
        bundle=output/'RealtekBluetoothFirmware.kext'
        binary=bundle/'Contents/MacOS/RealtekBluetoothFirmware'
        binary.parent.mkdir(parents=True)
        command=[compiler,'-arch','x86_64','-isysroot',str(sdk),'-nostdlib','-fapple-kext',
                 '-Xlinker','-kext','-L'+str(sdk/'usr/lib'),'-lkmodc++','-lkmod','-o',str(binary),*map(str,objects)]
        state['commands'].append(command)
        with (output/'link.log').open('wb') as log:
            subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
        info=plistlib.loads((source/'RealtekBluetoothFirmware/Info.plist').read_bytes())
        matching={k:v for k,v in info['IOKitPersonalities'].items() if v.get('idVendor')==0x0bda and v.get('idProduct')==0x4852}
        assert len(matching)==1
        info['IOKitPersonalities']=matching
        info['LocalHardwareScope']='ThinkPad E14 Gen3 AMD; Realtek USB 0bda:4852 only'
        (bundle/'Contents/Info.plist').write_bytes(plistlib.dumps(info,sort_keys=False))
        subprocess.run(['/usr/bin/codesign','--force','--sign','-','--timestamp=none',str(bundle)],check=True)
        subprocess.run(['/usr/bin/codesign','--verify','--strict','--verbose=2',str(bundle)],check=True)
        state.update(state='compiled_signed_not_installed',bundle=str(bundle),binary_sha256=sha(binary),
                     binary_uuid=subprocess.check_output(['/usr/bin/dwarfdump','--uuid',str(binary)],text=True).split()[1])
        print('Compilado, assinado e NÃO instalado:',bundle,flush=True)
    except BaseException as error:
        state.update(state='failed',error=str(error))
        raise
    finally:
        (output/'estado.json').write_text(json.dumps(state,indent=2)+'\n')
        print('Resultado:',output/'estado.json',flush=True)


if __name__=='__main__':
    main()
