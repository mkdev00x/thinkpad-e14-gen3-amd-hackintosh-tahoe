# Créditos, fontes e licenças

A licençaMIT na raiz cobre somente a documentação original e os helpers
originais deste repositório. Não substitui as licenças dos drivers, firmwares,
headers ou binários de terceiros.

## Fontes incluídas

| Componente | Origem e aviso |
| --- | --- |
| NootedRed e adaptação local 0.9.2 | [ChefKissInc/NootedRed](https://github.com/ChefKissInc/NootedRed), base de pesquisa[steve12311/NootedRed](https://github.com/steve12311/NootedRed); licença original ThouShaltNotProfit1.5 em[source/NootedRed/LICENSE](source/NootedRed/LICENSE). Modificações identificadas emMODIFICATIONS.md e sujeitas à mesma licença. |
| Firmware utilizado por NootedRed | Créditos/licenças preservados em[source/NootedRed/NootedRed/Firmware](source/NootedRed/NootedRed/Firmware). |
| RealtekBluetoothFirmware | [thegwchr/RealtekBluetoothFirmware](https://github.com/thegwchr/RealtekBluetoothFirmware), GPL-2.0-or-later;[LICENSE](source/RealtekBluetoothFirmware/LICENSE), avisos de seus componentes e fontes/firmware preservados. |
| Lilu | [acidanthera/Lilu](https://github.com/acidanthera/Lilu);[LICENSE.txt](source/dependencies/Lilu/LICENSE.txt) e avisos dos componentes internos preservados. |
| MacKernelSDK | [acidanthera/MacKernelSDK](https://github.com/acidanthera/MacKernelSDK);[LICENSE.txt](source/dependencies/MacKernelSDK/LICENSE.txt) e avisos dos headers preservados. |

## Outros componentes do perfilEFI

| Componente | Versão | Projeto/fonte |
| --- | --- | --- |
| OpenCore, OpenRuntime eOpenShell | 1.0.8 | [acidanthera/OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) |
| OpenHfsPlus | Binário do perfil | [acidanthera/OcBinaryData](https://github.com/acidanthera/OcBinaryData) |
| Lilu | 1.7.2 | [acidanthera/Lilu](https://github.com/acidanthera/Lilu) |
| VirtualSMC/SMCBatteryManager | 1.3.8 | [acidanthera/VirtualSMC](https://github.com/acidanthera/VirtualSMC) |
| ForgedInvariant | 1.5.0 | [ChefKissInc/ForgedInvariant](https://github.com/ChefKissInc/ForgedInvariant) |
| RestrictEvents | 1.1.6 | [acidanthera/RestrictEvents](https://github.com/acidanthera/RestrictEvents) |
| NVMeFix | 1.1.3 | [acidanthera/NVMeFix](https://github.com/acidanthera/NVMeFix) |
| AppleALC | 1.9.8 | [acidanthera/AppleALC](https://github.com/acidanthera/AppleALC) |
| SimpleHDA | 1.0.0 | [laobamac/SimpleHDA](https://github.com/laobamac/SimpleHDA) |
| RealtekRTL8111 | 3.0.4 | [Mieze/RTL8111_driver_for_OS_X](https://github.com/Mieze/RTL8111_driver_for_OS_X) |
| VoodooPS2Controller eplugins | 2.3.7 | [acidanthera/VoodooPS2](https://github.com/acidanthera/VoodooPS2) |
| VoodooInput | 1.1.6 | [acidanthera/VoodooInput](https://github.com/acidanthera/VoodooInput) |
| AirPort_RTW89 /front | 0.4.0, revisão3b49703 | [FranciumOS-org/Airport_RTW89](https://github.com/FranciumOS-org/Airport_RTW89); créditos e licença preservados no bundle, incluindo licença do firmwareRealtek. |
| BlueToolFixup | 2.7.2 | [acidanthera/BrcmPatchRAM](https://github.com/acidanthera/BrcmPatchRAM); pacoteRELEASE, assinatura ad hoc local com instruções preservadas. |
| IOSkywalkFamily/IO80211FamilyLegacy | Versões do manifesto | ComponentesApple utilizados como dependências da pilha Wi-Fi; referência[OpenCore Legacy Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher). Não são cobertos pela licençaMIT deste repositório. |
| USBMap-XHB1 | 1.0.0 | Mapa local codeless; formato documentado por[USBMap](https://github.com/corpnewt/USBMap). |

Os hashes e versões precisos dos bundles estão em`profiles/thinkpad-e14-gen3-amd.json`.
Os avisos presentes nos arquivos de terceiros foram preservados. A inclusão de
uma fonte não significa que seus autores endossem este perfil ou sua adaptação.

## Ferramentas de investigação

[REA](https://rea.tools/pt-BR/) e[Ghidra](https://github.com/NationalSecurityAgency/ghidra)
foram usados durante o diagnóstico. Seus instaladores e bases privadas de análise
não estão incluídos. Análise estática foi distinguida de execução/teste real.
