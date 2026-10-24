#!/usr/bin/env python3
"""Personaliza uma cópia local; não monta nem grava partições."""
import argparse
import json
from pathlib import Path
import plistlib
import re
import shutil
import uuid

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--identity',required=True,type=Path)
    args = parser.parse_args()
    identity = json.loads(args.identity.read_text())
    serial,mlb = identity['SystemSerialNumber'],identity['MLB']
    if not re.fullmatch(r'[A-Z0-9]{8,14}',serial) or serial.startswith('SEU'):
        raise ValueError('Serial inválido; gere uma identidade própria.')
    if not re.fullmatch(r'[A-Z0-9]{17}',mlb):
        raise ValueError('MLB precisa ter17caracteres alfanuméricos.')
    system_uuid = uuid.UUID(identity['SystemUUID'])
    rom = identity['ROM'].replace(':','').replace('-','')
    if not system_uuid.int or not re.fullmatch(r'[0-9a-fA-F]{12}',rom) or int(rom,16) == 0:
        raise ValueError('UUID/ROM inválido ou zerado.')
    target = ROOT/'EFI-private'
    if target.exists():
        raise FileExistsError('EFI-private já existe; nenhuma cópia será sobrescrita.')
    config = plistlib.loads((ROOT/'EFI/OC/config.plist').read_bytes())
    generic = config['PlatformInfo']['Generic']
    generic.update(SystemSerialNumber=serial,MLB=mlb,SystemUUID=str(system_uuid).upper(),ROM=bytes.fromhex(rom))
    shutil.copytree(ROOT/'EFI',target)
    (target/'OC/config.plist').write_bytes(plistlib.dumps(config,sort_keys=False))
    print('Cópia local preparada em EFI-private/. Valide-a com ocvalidate1.0.8 antes de usar.')
    print('Nenhuma partição foi montada ou alterada. Não publique sua identidade.')


if __name__ == '__main__':
    main()
