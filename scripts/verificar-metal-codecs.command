#!/bin/bash
set -euo pipefail
PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$PROJECT/diagnosticos/metal-codecs-terminal-$(date +%Y%m%d-%H%M%S)-$$"
PROBE="$PROJECT/bin/probe-metal-codecs"
EXPECTED='4ab0b5df048dd7db0514b1ebc42422af1d3ef831bdd64418505b3cb06b4b1021'
ACTUAL="$(/usr/bin/shasum -a 256 "$PROBE")"
[[ "${ACTUAL%% *}" == "$EXPECTED" ]] || { echo 'Helper alterado desde a preparação.'; exit 1; }
mkdir -p "$OUT"
echo 'Consultar Metal e codecs no contexto do Terminal. Sem sudo ou alterações de configuração.'
echo 'Não executa comandos Metal nem decodifica frames.'
/usr/bin/python3 - "$PROBE" "$OUT" <<'PY'
import json
from pathlib import Path
import subprocess
import sys
probe, output = sys.argv[1], Path(sys.argv[2])
try:
    result = subprocess.run([probe], capture_output=True, text=True, timeout=30)
    (output / 'metal-codecs.txt').write_text(result.stdout)
    (output / 'probe-stderr.txt').write_text(result.stderr)
    (output / 'probe-estado.json').write_text(json.dumps({'returncode':result.returncode, 'context':'normal_user_terminal'}, indent=2)+'\n')
    print(result.stdout, end='')
except subprocess.TimeoutExpired:
    (output / 'probe-estado.json').write_text(json.dumps({'state':'timeout', 'context':'normal_user_terminal'}, indent=2)+'\n')
    print('Consulta excedeu 30 segundos; estado registrado.')
PY
/usr/sbin/ioreg -r -c IOAccelerator -l -w0 > "$OUT/acelerador.txt"
/usr/sbin/ioreg -r -c NootedRed -l > "$OUT/nootedred.txt"
echo 'Resultado:' "$OUT"
echo 'Esses dados consultam capacidade; não substituem teste de vídeo/estabilidade.'
