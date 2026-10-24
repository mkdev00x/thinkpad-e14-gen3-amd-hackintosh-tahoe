#!/usr/bin/env python3
"""Somente leitura: rádio, transporte Bluetooth, portas USB e drivers carregados."""
from concurrent.futures import ThreadPoolExecutor
import datetime
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def usb_devices(text):
    devices = []
    for block in re.split(r'(?m)^.*\+-o ', text)[1:]:
        head = block.splitlines()[0]
        if 'class IOUSBHostDevice,' not in head:
            continue
        vendor = re.search(r'"idVendor" = (\d+)', block)
        product = re.search(r'"idProduct" = (\d+)', block)
        if vendor and product:
            device = {'node': head, 'vendor': int(vendor[1]), 'product': int(product[1]),
                      'usb_id': f'{int(vendor[1]):04x}:{int(product[1]):04x}'}
            firmware = re.search(r'"FirmwareLoaded" = (Yes|No|true|false)', block)
            if firmware:
                device['firmware_loaded'] = firmware[1] in ('Yes','true')
            product_name = re.search(r'"USB Product Name" = "([^"]+)"', block)
            revision = re.search(r'"RealtekInternalNameRevision" = (\d+)', block)
            if product_name:
                device['usb_product_name'] = product_name[1]
            if revision:
                device['internal_name_revision'] = int(revision[1])
            devices.append(device)
    return devices


def main():
    if sys.platform != 'darwin':
        raise RuntimeError('Execute no macOS instalado.')
    out = ROOT / 'diagnosticos' / ('bluetooth-terminal-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    out.mkdir()
    data_types = subprocess.check_output(['/usr/sbin/system_profiler', '-listDataTypes'], text=True, timeout=15)
    usb_type = 'SPUSBHostDataType' if 'SPUSBHostDataType' in data_types.split() else 'SPUSBDataType'
    cmds = {
        'bluetooth.txt': ['/usr/sbin/system_profiler', 'SPBluetoothDataType'],
        'usb.txt': ['/usr/sbin/system_profiler', usb_type],
        'usb-ioreg.txt': ['/usr/sbin/ioreg', '-p', 'IOUSB', '-l', '-w0'],
        'portas-usb.txt': ['/usr/sbin/ioreg', '-r', '-c', 'AppleUSBHostPort', '-l', '-w0'],
        'controladores-usb.txt': ['/usr/sbin/ioreg', '-r', '-c', 'AppleUSBXHCIPCI', '-l', '-w0'],
        'bluetooth-ioreg.txt': ['/usr/sbin/ioreg', '-r', '-c', 'IOBluetoothHCIController', '-l', '-w0'],
        'bluetooth-transporte.txt': ['/usr/sbin/ioreg', '-r', '-c', 'IOBluetoothHCIUSBTransport', '-l', '-w0'],
        'realtek-driver.txt': ['/usr/sbin/ioreg', '-r', '-c', 'RealtekBluetoothFirmware', '-l', '-w0'],
        'kexts.txt': ['/usr/bin/kmutil', 'showloaded'],
        'nvram-bluetooth-interno.txt': ['/usr/sbin/nvram', 'bluetoothInternalControllerInfo'],
        'nvram-bluetooth-externo.txt': ['/usr/sbin/nvram', 'bluetoothExternalDongleFailed'],
        'nootedred.txt': ['/usr/sbin/ioreg', '-r', '-c', 'NootedRed', '-l'],
        'log-bluetooth-usb.txt': ['/usr/bin/log', 'show', '--last', '10m', '--style', 'compact', '--predicate',
             '(process == "bluetoothd" OR process == "BlueTool") OR (process == "kernel" AND '
             '(eventMessage CONTAINS[c] "Bluetooth" OR eventMessage CONTAINS[c] "RealtekFirmware" '
             'OR eventMessage CONTAINS[c] "btlfx"))'],
    }

    def collect(item):
        name, cmd = item
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=40)
            (out / name).write_bytes(result.stdout)
            return name, result.returncode
        except subprocess.TimeoutExpired as error:
            (out / name).write_bytes(error.stdout or b'')
            return name, 'timeout'

    with ThreadPoolExecutor(max_workers=4) as pool:
        status = dict(pool.map(collect, cmds.items()))
    devices = usb_devices((out / 'usb-ioreg.txt').read_text(errors='replace'))
    summary = {'context': 'operator_terminal', 'commands': status, 'usb_devices': devices,
               'expected_realtek_0bda_4852_present': any(d['usb_id'] == '0bda:4852' for d in devices)}
    (out / 'resumo.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('Rádio Realtek 0bda:4852 encontrado no USB:', summary['expected_realtek_0bda_4852_present'])
    print('Dispositivos USB:', ', '.join(d['usb_id'] for d in devices) or 'nenhum enumerado nesta coleta')
    for radio in (d for d in devices if d['usb_id'] == '0bda:4852'):
        print('Firmware carregado:', radio.get('firmware_loaded', 'não informado'))
        print('Nome USB:', radio.get('usb_product_name', 'não informado'))
        print('Revisão do nome interno:', radio.get('internal_name_revision', 'não instalada'))
    print((out / 'bluetooth.txt').read_text(errors='replace'))
    if status['bluetooth.txt'] == 'timeout':
        print('A consulta do controlador Bluetooth excedeu 40 segundos; os logs foram preservados.')
    print('Resultado:', out)
    print('Nenhuma alteração em EFI, drivers, preferências ou firmware.')


if __name__ == '__main__':
    main()
