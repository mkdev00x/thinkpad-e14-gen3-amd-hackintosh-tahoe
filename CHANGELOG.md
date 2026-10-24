# Alterações

## 2026.10.24 — perfil validado

- Boot pelo SSD usando OpenCore 1.0.8 e macOS 26.7.1 / 25G241.
- NootedRed local 0.9.2: preservação da assinatura das páginas modificadas e patch
  restrito do emissor OpenGL; Sublime, Chrome e YouTube aprovados pelo usuário.
- Metal disponível; capacidade H.264/HEVC consultada no Terminal normal.
- Mapa USB interno XHB1 com portas 3/4 e rename ACPI de boot XHC1 → XHB1.
- RealtekBluetoothFirmware 1.0.2 e BlueToolFixup 2.7.2; seleção HCI genérica com
  as duas variáveis Bluetooth em NVRAM Add/Delete.
- AirPods pareados, conectados e reproduzindo música normalmente.
- Publicação com identidade SMBIOS removida, fontes locais, documentação e hashes.

### Tentativas superadas

- O candidato gráfico inicial falhou ao iniciar pelo SSD com InvalidPage.
- A versão local 0.9.1 passou no boot, mas ainda corrompia a tela ao abrir Sublime.
- O experimento Bluetooth local 1.0.3 publicava o nome Apple: abriu o USB, mas
  levou à inicialização Broadcom inadequada. Foi retirado do perfil final.

Essas tentativas estão documentadas como histórico técnico, não como opções para instalar.
