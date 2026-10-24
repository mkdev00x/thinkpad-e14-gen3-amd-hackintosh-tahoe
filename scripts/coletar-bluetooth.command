#!/bin/bash
set -euo pipefail
PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo 'Coleta de Bluetooth/USB no Terminal normal. Sem sudo e sem alterar configurações.'
exec /usr/bin/python3 "$PROJECT/scripts/coletar-bluetooth.py"
