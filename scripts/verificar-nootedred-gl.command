#!/bin/bash
set -euo pipefail
PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$PROJECT/diagnosticos/gl-verificacao-$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p "$OUT"
echo 'Verificação da página OpenGL. Não abre apps nem envia comandos à GPU.'
/usr/sbin/ioreg -r -c NootedRed -l > "$OUT/nootedred.txt"
/usr/sbin/ioreg -r -c IOPCIDevice -l -w0 > "$OUT/pci-antes.txt"
if ! /usr/bin/grep -q 'REL-092-' "$OUT/nootedred.txt"; then
    echo 'A versão local 0.9.2 não está carregada. Resultado:' "$OUT"
    exit 1
fi
if ! /usr/bin/grep -q '"NRedGLBlendEnabled" = 1' "$OUT/pci-antes.txt"; then
    echo 'O hook OpenGL não foi confirmado como ativo. Resultado:' "$OUT"
    exit 1
fi
PROBE="$PROJECT/bin/probe-gl-pagina"
EXPECTED='f24b9be5057184c6f80179e21ca69e3ad4b443f5f24e530c4cbe6b4a07a88c11'
ACTUAL="$(/usr/bin/shasum -a 256 "$PROBE")"
if [[ "${ACTUAL%% *}" != "$EXPECTED" ]]; then
    echo 'O helper mudou desde a preparação. Interrompido.'
    exit 1
fi
set +e
"$PROBE" > "$OUT/pagina.txt" 2>&1
RESULT=$?
set -e
/bin/cat "$OUT/pagina.txt"
# Um novo processo permite publicar os contadores fora do callback de VM.
/usr/bin/true
/usr/sbin/ioreg -r -c IOPCIDevice -l -w0 > "$OUT/pci-depois.txt"
echo "$RESULT" > "$OUT/probe-exit.txt"
echo 'Resultado:' "$OUT"
if [[ "$RESULT" -eq 0 ]]; then
    echo 'Bytes do patch observados em memória. Isso ainda não testa a GPU.'
else
    echo 'Patch não confirmado. Não repetir Sublime/Chrome antes de analisar o relatório.'
fi
exit "$RESULT"
