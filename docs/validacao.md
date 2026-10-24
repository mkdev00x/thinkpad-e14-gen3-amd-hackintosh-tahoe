# Validação do perfil

Data:24/10/2026. Hardware/build:ThinkPad E14 Gen 3 AMD, Ryzen 5 5500U, iGPU164c,
macOS 26.7.1/25G241. Evidências foram consolidadas para publicação sem identidade pessoal.

## Gráficos

| Verificação | Resultado |
| --- | --- |
| Boot com NootedRed 0.9.2 | Aprovado pelo SSD |
| Versão/UUID da kext | REL-092;26BFF949-0EE5-3844-8540-537CEB399349 |
| PáginaGLRX | Bytes`b90200000090` observados; registro de assinatura retornou0 |
| Falhas de escrita/restauraçãoGL | 0 no intervalo inicial observado |
| ContextoSublime | AMDGFX9GLContext com tempoGPU acumulado |
| Sublime Text 4215 | Digitar/mover/redimensionar por cerca de 30 s sem corrupção |
| Chrome 156 | Página/rolagem/movimento de janela normais no teste |
| YouTube | 1080p60 por cerca de 2 min e tela cheia, relatado fluido |
| Metal | DispositivoAMD disponível; famíliaMac2=true |
| VideoToolbox | H264/HEVC=true;VP9/AV1=false como capacidadeAPI |

A leitura da página foi novamente confirmada depois das mudançasBluetooth.
Não houve alteração de preferências para desativar aGPU dos aplicativos.
O decoder usado pelo vídeo específico não foi demonstrado pelos contadores amostrados.

## Bluetooth

| Verificação | Resultado |
| --- | --- |
| EnumeraçãoUSB | Realtek0bda:4852 na porta interna prevista |
| FirmwareLoaded | true; imagem `rtl8852au` |
| Loader | RealtekBluetoothFirmware 1.0.2, UUID8E67E677-4492-3BE8-9C2C-C479681A918B |
| BlueToolFixup | 2.7.2, UUID037F9890-9A93-3E7F-AC9B-4AD018E0A67B |
| SeleçãoHCI | THIRD_PARTY_DONGLE / USB |
| Controlador | On e endereço válido, omitido da publicação |
| Firmware anunciado | v6106c55766 |
| FalhaHCI anterior | 0 ocorrências no intervalo observado do novo boot |
| AirPods | Usuário confirmou conexão e música normal |

## Verificação da cópia publicada

A árvore EFI foi comparada com o manifesto gerado durante a publicação real do
perfil noSSD. A cópia pública conserva os binários funcionais, mas remove:

- serial/MLB/UUID/ROM pessoais;
- ferramenta de resgateLinux particular e sua entrada;
- backup antigo do config contendo identidade.

Não se trata de uma leitura nova da partiçãoEFI: é a staging cujos bytes foram
confirmados pelo instalador no momento da publicação. Todos os hashes públicos
se referem à cópia já anonimizada, não ao config privado original.

`ocvalidate`1.0.8 validou o perfil. `validar-repositorio.py` confere hashes,
referências de arquivos, identidade removida e as opções essenciais do perfil.

## Limites

Não foram feitos benchmark quantitativo, teste prolongado, ciclo de repouso,
validação de microfoneAirPods/HDMI/DRM ou medição de autonomia. A afirmação de
funcionamento refere-se aos testes acima.

ConsultasMetal/Bluetooth no executor restrito chegaram a devolvernil/dicionário
vazio. O controle no Terminal normal e os testes reais deram resultado positivo.
Uma consulta restrita vazia, sozinha, não justifica mudar a configuração funcional.
