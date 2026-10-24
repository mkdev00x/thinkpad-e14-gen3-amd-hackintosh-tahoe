# Preparação e uso da EFI

Este é um perfil de pós-instalação. O macOS de referência já estava instalado;
nenhum script deste repositório formata discos, cria APFS ou reinstala o sistema.

## Antes de usar

Confira o modelo, PCIIDs, build 25G241 e o mapa físico das portas da sua unidade.
O patch gráfico local usa bytes e páginas específicos desse driver do Tahoe.
Preserve a EFI que já inicia o computador e um meio de recuperar esse boot.

O `SecureBootModel` do OpenCore está Disabled no perfil de referência. A configuração
também contém `-amfipassbeta`, os patchesAMD e as demais opções já usadas no ambiente
validado. Isso documenta o estado real; não demonstra suporte com outras opções.

## Identidade SMBIOS

A EFI pública utiliza `iMac20,1` e **não contém uma identidade utilizável**.
Gere dados próprios com [GenSMBIOS](https://github.com/corpnewt/GenSMBIOS) e
consulte o [guia OpenCore](https://dortania.github.io/OpenCore-Install-Guide/).

Guarde os valores em um arquivo fora do repositório, por exemplo:

```json
{
  "SystemSerialNumber": "SEU_SERIAL",
  "MLB": "SEU_MLB",
  "SystemUUID": "SEU_UUID",
  "ROM": "SEU_ROM_HEXADECIMAL_12_DIGITOS"
}
```

Depois crie a cópia local:

```bash
python3 scripts/preparar-efi-local.py --identity /caminho/identidade.json
```

Ela será gravada em`EFI-private/`, ignorado pelo Git. O comando se recusa a
sobrescrever uma pasta existente e não monta/grava partições.
Mantenha o arquivo de identidade fora da publicação.

## Validação e boot

1. Execute `python3 scripts/validar-repositorio.py` na referência intacta.
2. Valide `EFI-private/OC/config.plist` usando `ocvalidate`1.0.8 do pacote oficial
   [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg/releases).
3. Confira Kernel/Add, dependências, arquivosACPI e ordem das kexts.
4. Teste a cópia em um meio de boot que permita retornar à EFI anterior.
5. Somente depois considere copiá-la para o SSD correto, identificado no seu Mac.

Identificadores `diskN` variam. Não foi publicado um instalador que suponha o
mesmo SSD, UUID ou particionamento do notebook de desenvolvimento.
O resgate Linux personalizado daquele ambiente foi removido da cópia pública.
As partições existentes e seu boot anterior não são alterados pelas ferramentas daqui.

## Confirmar depois do boot

```bash
bash scripts/verificar-nootedred-gl.command
bash scripts/verificar-metal-codecs.command
bash scripts/coletar-bluetooth.command
```

Confirme primeiro a versão0.9.2 local e os bytes OpenGL esperados, depois teste
Sublime/Chrome e vídeo. Para Bluetooth, espere endereço válido, estadoOn e
`THIRD_PARTY_DONGLE`; só então teste pareamento e áudio.
