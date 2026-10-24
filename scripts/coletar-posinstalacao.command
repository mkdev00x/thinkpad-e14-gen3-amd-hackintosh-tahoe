#!/bin/bash
# Collect current installed macOS state without changing disks, EFI or drivers.
set -u
[[ "$(uname -s)" == Darwin ]] || { echo 'Execute no macOS instalado.' >&2; exit 1; }
PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$PROJECT/diagnosticos/macos-$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p "$OUT" || exit 1
collect() {
  local file="$1" result
  shift
  "$@" > "$OUT/$file" 2>&1
  result=$?
  printf '%s\t%s\n' "$file" "$result" >> "$OUT/retornos.tsv"
}
collect sistema.txt sw_vers
collect hardware-grafico-audio.json system_profiler SPHardwareDataType SPDisplaysDataType SPAudioDataType -json
collect gpu.txt system_profiler SPDisplaysDataType
collect audio.txt system_profiler SPAudioDataType
collect kextstat.txt kextstat
collect kmutil.txt kmutil showloaded
collect acelerador.txt ioreg -r -c IOAccelerator -l
collect nootedred.txt ioreg -r -c NootedRed -l
collect chosen.txt ioreg -p IODeviceTree -n chosen -r -l
collect motores-audio.txt ioreg -r -c IOAudioEngine -l
collect hdef.txt ioreg -r -n HDEF -l
collect hdas.txt ioreg -r -n HDAS -l
collect pci.txt ioreg -r -c IOPCIDevice -l
collect boot-cpu.txt sysctl kern.bootargs machdep.cpu.brand_string hw.ncpu hw.physicalcpu hw.logicalcpu hw.memsize
collect applehda-presenca.txt ls -ld /System/Library/Extensions/AppleHDA.kext /Library/Extensions/AppleHDA.kext
collect coremedia.txt defaults read /Library/Preferences/com.apple.coremedia allowMetalTransferSession
collect energia.txt pmset -g custom
collect discos.txt diskutil list
collect apfs.txt diskutil apfs list
collect log-gpu-audio.txt log show --last 10m --style compact --predicate 'process == "kernel" AND (eventMessage CONTAINS[c] "Nooted" OR eventMessage CONTAINS[c] "AppleALC" OR eventMessage CONTAINS[c] "AppleHDA" OR eventMessage CONTAINS[c] "AMDRadeon")'
printf 'Coleta somente de leitura do macOS instalado.\nArquivos com comando indisponivel ou sem permissao preservam o erro e o retorno; isso nao prova defeito.\nNao altera EFI, SIP, NVRAM ou volume selado.\n' > "$OUT/LEIA-ME.txt"
echo "Diagnostico salvo em: $OUT"
echo 'Revise os dados pessoais antes de compartilhar a coleta.'
