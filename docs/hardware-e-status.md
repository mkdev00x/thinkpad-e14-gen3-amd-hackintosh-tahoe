# Hardware e validação

O perfil foi validado em uma unidade ThinkPad E14 Gen 3 AMD, tipo 20YD, com Ryzen 5
5500U/Lucienne e iGPU1002:164c. A memória instalada é16 GB; o driver anuncia4 GB
gráficos. O nome exibido pela API Metal é `AMD Radeon RX Renoir Graphics`.

Não confundir esse nome com uma placa dedicada: o hardware deste notebook é integrado.

| Item | Evidência ou estado |
| --- | --- |
| macOS | 26.7.1, build 25G241, Darwin 25.6.0 |
| OpenCore | 1.0.8; perfil `iMac20,1` |
| CPU | Ryzen 5 5500U, 6C/12T; patchesAMD preservados no config |
| Metal | MTLCreateSystemDefaultDevice retornou o dispositivoAMD; famíliaMac2=true |
| OpenGL | Contexto AMDGFX9GLContext do Sublime observado com tempoGPU acumulado |
| Chrome/Sublime/YouTube | Testes reais relatados como normais pelo usuário |
| Wi-Fi | RTL8852AE/10ec:8852; AirPort_RTW89 0.4.0 |
| Bluetooth | USB 0bda:4852; firmware `rtl8852au`; backend HCIgenérico |
| AirPods | Conectados e reproduzindo música normalmente |
| Áudio integrado | ALC257/layout 11 e SimpleHDA/AppleALC configurados; teste específico separado dos AirPods |
| USB interno | Goodix27c6:5503 na porta 3; Bluetooth0bda:4852 na porta 4 |
| Teclado/trackpad | VoodooPS2Controller no perfil; gestos não inventariados nesta rodada |
| Ethernet | RealtekRTL8111 no perfil; desempenho/cabo não medidos nesta rodada |
| Bateria | SMCBatteryManager incluído; autonomia não medida |
| HDMI/USB-C vídeo | Não validados nesta rodada |
| Repouso/retomada | Não validado nesta rodada |
| Leitor de digitais | Dispositivo USB detectado; autenticação não validada |
| DRM/AirDrop/Continuidade | Não validados neste perfil |

Os resultados se referem ao build acima e ao hardware indicado. A identificação
de uma kext carregada, de uma GPU ou de um dispositivoUSB não substitui teste funcional.

Detalhes das versões e hashes: [perfil JSON](../profiles/thinkpad-e14-gen3-amd.json).
