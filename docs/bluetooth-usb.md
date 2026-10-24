# USB e Bluetooth Realtek

## Hardware

Wi-Fi RTL8852AE/PCI 10ec:8852 e BluetoothUSB 0bda:4852 são funções diferentes.
Este procedimento trata o rádioUSB, que usa firmware `rtl8852au`.

## 1. Recuperar a porta interna

O SMBIOS iMac20,1 fazia o perfilUSB nativoApple corresponder ao controlador XHC1
do ThinkPad. Esse mapa incluía o leitorGoodix na porta 3, mas não a porta 4 do Bluetooth.

O perfil final aplica no ACPI de boot:

```text
XHC1 → XHB1
58 48 43 31 → 58 48 42 31
```

`USBMap-XHB1.kext`, codeless, usa AppleUSBHostMergeProperties e combina
SMBIOS iMac20,1 com IONameMatchXHB1. PortasHS03/HS04 são internas, conector 255,
com port-count 4. XHC0, usado pelos dispositivos externos, permanece sem esse mapa.

Essa é uma alteração da configuração de boot, não um flash de firmware/BIOS.
O mapa é específico da enumeração observada neste modelo.

## 2. Firmware e compatibilidade

- RealtekBluetoothFirmware 1.0.2, fonte`thegwchr/RealtekBluetoothFirmware`, commit
  `22e501a8a0a7aba8bb4e594bc6f40b1a67391af9`.
- Compilação local com personalidadeIOKit restrita a0bda:4852.
- Imagem`rtl8852au_fw.bin`:67188 bytes, SHA256
  `56be2eb99d36109bb5e01eee171573b6f3dd041238c01cd97ce4f01df8dbf09e`.
- BlueToolFixup 2.7.2, pacote oficialBrcmPatchRAM, assinado ad hoc localmente sem
  alterar as instruções da release.
- Lilu carregada antes do BlueToolFixup; NootedRed 0.9.2 preservada.

O loader identifica HCI/ROM em execução e carrega firmware apropriado em RAM.
Os testes do parser e a imagem embutida foram conferidos na investigação.
Não foi aplicado firmware de chip diferente nem alterada a BIOS.

## 3. Selecionar o backend genérico

No GUID `7C436110-AB2A-4BBB-A880-FE41995C9F82`, em NVRAM/Add:

| Chave | Tipo | Dados |
| --- | --- | --- |
| bluetoothExternalDongleFailed | Data | 1 byte zero |
| bluetoothInternalControllerInfo | Data | 14 bytes zero |

As mesmas duas chaves constam em NVRAM/Delete para os valores serem reaplicados
no boot. Isso não é um ResetNVRAM global.

O executável do build 25G241 exige CFData de 14 bytes para a informação interna e
permite a detecção com o indicador de falha zerado. Found_USB_Dongle reconhece
as interfacesRealtek e o sistema escolhe tipo 0/`THIRD_PARTY_DONGLE`, usandoHCIgenérico.

Essas variáveis são tratadas na documentação do
[BlueToolFixup](https://github.com/acidanthera/BrcmPatchRAM#bluetoolfixupkext).
A contagem14 foi conferida no binário deste Tahoe, não inferida de uma sequência
hexadecimal ilustrativa de outro build.

## A tentativa de nome Apple foi descartada

O experimento local 1.0.3 alterava `USB Product Name` para`Bluetooth USB Host Controller`.
Isso fez o caminho interno abrir oUSB, mas também fez a detecção genérica ignorar
o rádio. O daemon assumiaBCM4350C2 e falhava no comandoVSCReadVerboseConfigVersion.

O perfil final usa o loader 1.0.2 original, sem essa alteração de propriedade.
**`USB Product Name=Bluetooth Radio` é correto.** A entrada na árvoreIORegistry
pode continuar chamada`Bluetooth USB Host Controller`; são campos distintos.

## Resultado real

- RádioUSB visível eFirmwareLoaded=true;
- controladorOn, endereçoBluetooth válido, backendTHIRD_PARTY_DONGLE eUSB;
- firmwarev6106c55766;
- nenhuma repetição da falhaHCI anterior no intervalo observado do novo boot;
- AirPods pareados, conectados e reproduzindo música normalmente.

`Discoverable:Off` não impediu o pareamento testado. `VendorID:Apple` no resumo
genérico do sistema não muda oVID/PID real0bda:4852.

REA/Ghidra descompilou um recorte da função de seleção, delimitado por
LC_FUNCTION_STARTS; o assembly completo correlacionou nomes/tabelas. Chamadas
e dados externos ao recorte continuaram como limitações da análise estática.

```bash
bash scripts/coletar-bluetooth.command
```

NoTahoe, a enumeraçãoUSB usaSPUSBHostDataType quando disponível.
Erros antigos nos10minutos de logs podem pertencer ao boot anterior; compare
timestamps antes de interpretar uma regressão.
