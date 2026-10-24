# Fontes e compilação

## Componentes locais

As fontes completas das duas compilações locais estão em`source/`.
NootedRed inclui a adaptação de assinatura/OpenGL; RealtekBluetoothFirmware
é o upstream1.0.2, com personalidadeIOKit do pacote restrita a0bda:4852.

As dependências exportadas de Lilu e MacKernelSDK mantêm seus avisos/licenças.
`source/dependencies/versions.json` registra commits e hashes dos arquivos
usados pela receita. Não é necessário executar scripts de instalação upstream.

| Fonte | Revisão |
| --- | --- |
| NootedRed, base de pesquisa | `7a81e78b1a40ee01ada721be1b84431585b7457b` + adaptações locais0.9.2 |
| Lilu, headers/plugin_start | `0515f40b7f2a096adc85e832a4c6104fbd07f936` |
| MacKernelSDK | `7af1933c27aefcbdf4809ee44478829aad30f9c1` |
| RealtekBluetoothFirmware | `22e501a8a0a7aba8bb4e594bc6f40b1a67391af9` |
| BlueToolFixup/BrcmPatchRAM | release2.7.2; fonte`aef376bb1e7e27cabc61da7edfb1a88fac7f7acc` |

NootedRed 0.9.2 é uma versão local: o número não identifica uma release oficial
de ChefKiss ou de outro fork. Consulte[MODIFICATIONS.md](../source/NootedRed/MODIFICATIONS.md).

## Compilar sem instalar

Ambiente usado na investigação: macOS x86_64 com CommandLineTools/clang 21,
Kernel.framework do SDK local e dependências acima. As receitas escrevem em`build/`.

```bash
python3 scripts/compilar-nootedred.py
python3 scripts/compilar-realtek.py
```

Elas compilam e assinam ad hoc os bundles locais; não copiam paraEFI nem carregam
kexts. Confira os logs, versão, assinatura, símbolos e instruções antes de usar
qualquer recompilação. Uma assinatura ad hoc não é assinatura de desenvolvedorApple.

Os binários no perfil são os bytes já validados no notebook. O mesmo fonte em
outra versão deSDK/compilador pode produzir hash/UUID diferente; isso não deve
ser apresentado como reprodução byte a byte sem comparação.

Na preparação desta publicação, as duas receitas foram executadas novamente
em uma pasta independente. **NootedRed e Realtek recompilaram com bytes eSHA256
idênticos aos binários funcionais incluídos.** O resultado e o compilador estão
em [profiles/reproducao.json](../profiles/reproducao.json). Nada foi instalado na EFI.

## TestesCPU e consultas

```bash
python3 scripts/testar-gl-dualquad-cpu.py
python3 scripts/testar-gl-validacao-cpu.py
```

O teste do emissor extrai bytes do driverGL local apenas se seuSHA corresponder
ao buildvalidado. As chamadas de submissão GPU são bloqueadas comUD2 no teste.
O teste do wrapper usa stubs e buffers locais; não instala código no kernel.

Se o hookGL já estiver ativo, a leitura pode conter os 6 bytes alterados no cache
unificado. O teste reverte esses6bytes somente em seu buffer local e exige o
SHA original completo antes de prosseguir. Não grava o arquivo nem a página do driver.

Os helpers de `bin/` correspondem aos fontes `probe-gl-pagina.cpp` e
`probe-metal-codecs.mm`. O primeiro apenas registra a assinatura original e lê
uma páginaRX; o segundo consulta APIs de capacidade sem submeter comandosMetal
ou decodificar frames. Os wrappers conferem seus hashes antes de executá-los.

## REA e Ghidra

A investigação usou REA 6.7.0 e Ghidra 12.1.4 no Mac para inspecionar o emissorGL,
wrappers da kext e seleção do backendBluetooth. O daemon inteiro excedeu o
prazo de análise; a função de seleção foi analisada em um recorte delimitado
porLC_FUNCTION_STARTS e correlacionada com oassembly completo.

Pseudocódigo não é fonte original nem prova de execução. Algumas chamadas
virtuais e saídas de funções foram reconstruídas com limitações; oassembly
foi consultado para resolver os pontos relevantes. Os relatórios privados
brutos não foram publicados; as conclusões e seus limites estão nos guias.
