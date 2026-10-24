# Gráficos: a correção local

## Sintoma e resultado

Abrir Sublime Text 4 corrompia a tela inteira e podia exigir desligamento forçado.
O Chrome também estava no escopo da falha. Mostrar Radeon e memória gráfica
no sistema não demonstrava que esses aplicativos funcionariam.

O candidato inicial de pesquisa falhou no boot por assinatura de página
modificada. A adaptação local 0.9.1 passou no boot, mas não resolveu o emissor
OpenGL utilizado pelo Sublime. A versão local 0.9.2 acrescentou a correçãoGL.

Após instalar0.9.2, o usuário validou Sublime com digitação/movimento/redimensionamento,
Chrome normal e YouTube 1080p60/tela cheia fluido, sem reproduzir a corrupção.

## Base e perfil

- Base: `steve12311/NootedRed`, commit`7a81e78b1a40ee01ada721be1b84431585b7457b`.
- Adaptações locais: assinatura das páginas e correção OpenGL, versão0.9.2.
- Hardware: PCI 1002:164c, Darwin 25.6, build 25G241.
- Flags existentes: `-NRedDisplayFix -NRedVideoFix`.
- SHA256 da kext funcional: `a027580b31da29a37a5bd4a62fa64ce65e3aa5140a9ac0f2dbdf0a5fc7209fa1`.
- UUID: `26BFF949-0EE5-3844-8540-537CEB399349`.

É uma compilação local, não uma release oficial ou uma recomendação para builds diferentes.

## Patch OpenGL

Alvo instalado:

```text
/System/Library/Extensions/AMDRadeonX5000GLDriver.bundle/Contents/MacOS/AMDRadeonX5000GLDriver
SHA256 ce205f063627a4b82ee8ccee04ab7963a3efb8dec488cb3c53ed6c6719434f80
Função _glrAMD_GFX9_UpdateHwCbDualQuadMode, RVA 0x819e
Alteração RVA 0x81b9: 8b88a0000000 → b90200000090
```

O emissor original condicionava um bit de CB_COLOR_CONTROL a uma capacidade
selecionada pelas classesVega dGPU. A alteração deixa esse bit acompanhar o
uso de dual-source blending no alvo testado, preservando os outros bits.

A aplicação usa `_cs_validate_page` com a ABI real de sete argumentos e retorno
void. Chama o original primeiro, exige validação/taint/NX esperados, offset 0x8000
e comparação dos 4096 bytes da página original. Altera somente 6 bytes sob a trava
de escrita Lilu. O callback não faz filesystem, IORegistry, alocação ou logging.

O arquivo Apple e o volume selado não são regravados por esse patchGL.
As fontes incluem também as adaptações anteriores de assinatura e Metal/VCN
herdadas da base, sem desativar a aceleração dos aplicativos.

## Evidências

- REA/Ghidra analisou o emissorApple e os wrappers compilados da kext local.
- Teste CPU: 65536 casos; chamadas de submissão substituídas porUD2 nos emissores
  usados no teste. Nenhum comando GPU foi submetido por esse teste.
- Wrapper com mocks: encaminhamentoABI, gates, idempotência, escrita exata,
  restauração e falhas/concorrência exercitados sem executar kernel.
- PáginaRX observada com `b90200000090`, contadores de aplicação e falhas0.
- Sublime apresentou contextoAMDGFX9GLContext com tempoGPU acumulado.
- Consultas no Terminal confirmaram Metal e famíliaMac2.

```bash
python3 scripts/testar-gl-dualquad-cpu.py
python3 scripts/testar-gl-validacao-cpu.py
bash scripts/verificar-nootedred-gl.command
```

Os dois primeiros testes usam CPU/buffers de teste e exigem CLT; o primeiro
confere o hash do driver local antes de extrair a função. O terceiro apenas
mapeia/lê a páginaRX do driver e não executa seu código.

## Codecs e limites

H.264/HEVC anunciaram suporte de hardware naAPI VideoToolbox; VP9/AV1 não.
Essa consulta não decodifica frames. Os contadores amostrados não comprovaram
o decoder GPU no vídeo específico do YouTube, embora o teste tenha sido fluido.

Testes funcionais e consultas são evidências diferentes. Não há benchmark
quantitativo ou promessa de estabilidade em qualquer aplicativo/build.
