#!/usr/bin/env python3
"""Valida o perfil público sem acessar hardware, rede ou discos do sistema."""
import ast
import hashlib
import json
from pathlib import Path
import plistlib

ROOT = Path(__file__).resolve().parents[1]
GUID = '7C436110-AB2A-4BBB-A880-FE41995C9F82'


def main():
    manifest = json.loads((ROOT/'manifesto-publico.json').read_text())
    for relative,digest in manifest['files'].items():
        path = ROOT/relative
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Arquivo divergente: '+relative)
    config = plistlib.loads((ROOT/'EFI/OC/config.plist').read_bytes())
    generic = config['PlatformInfo']['Generic']
    assert generic['SystemProductName'] == 'iMac20,1'
    assert all(generic[k] == '' for k in ('MLB','SystemSerialNumber','SystemUUID'))
    assert generic['ROM'] == bytes(6), 'Identidade pessoal não pode entrar na EFI pública.'
    assert config['NVRAM']['Add'][GUID]['bluetoothExternalDongleFailed'] == bytes(1)
    assert config['NVRAM']['Add'][GUID]['bluetoothInternalControllerInfo'] == bytes(14)
    for key in ('bluetoothExternalDongleFailed','bluetoothInternalControllerInfo'):
        assert key in config['NVRAM']['Delete'][GUID]
    bundles = [e['BundlePath'] for e in config['Kernel']['Add'] if e['Enabled']]
    assert bundles.index('Lilu.kext') < bundles.index('NootedRed.kext') < bundles.index('AppleALC.kext')
    assert bundles.index('Lilu.kext') < bundles.index('BlueToolFixup.kext')
    assert 'WhateverGreen.kext' not in bundles
    for entry in config['Kernel']['Add']:
        if entry['Enabled']:
            root = ROOT/'EFI/OC/Kexts'/entry['BundlePath']
            for key in ('PlistPath','ExecutablePath'):
                if entry[key]:
                    assert (root/entry[key]).is_file(), str(root/entry[key])
    for entry in config['ACPI']['Add']:
        if entry['Enabled']:
            assert (ROOT/'EFI/OC/ACPI'/entry['Path']).is_file()
    for entry in config['UEFI']['Drivers']:
        if entry['Enabled']:
            assert (ROOT/'EFI/OC/Drivers'/entry['Path']).is_file()
    assert all(t['Path'] != 'LinuxRescue.efi' for t in config['Misc']['Tools'])
    assert not (ROOT/'EFI/OC/config-antes-audio.plist').exists()
    info = plistlib.loads((ROOT/'EFI/OC/Kexts/RealtekBluetoothFirmware.kext/Contents/Info.plist').read_bytes())
    personality, = info['IOKitPersonalities'].values()
    assert info['CFBundleVersion'] == '1.0.2'
    assert personality['idVendor'] == 0x0bda and personality['idProduct'] == 0x4852
    for path in (ROOT/'scripts').glob('*.py'):
        ast.parse(path.read_text())
    print('OK: hashes, identidade removida, referências EFI, ordem das kexts, Bluetooth e sintaxePython.')


if __name__ == '__main__':
    main()
