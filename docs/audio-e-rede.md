# Áudio e rede

## Áudio integrado

O codec real é Realtek ALC257. O perfil usa `alcid=11`, AppleALC 1.9.8 e
SimpleHDA 1.0.0, com Lilu 1.7.2 e `keepsyms=1`. A ordem relativa permanece
Lilu → NootedRed → AppleALC → SimpleHDA.

O Tahoe deste ambiente não contém AppleHDA.kext no caminho de sistema.
SimpleHDA é o componente incluído no perfil para restaurar a pilha AppleHDA
por injeção; apenas trocar o layoutAppleALC não supriria uma pilha ausente.

Documentação do projeto: [laobamac/SimpleHDA](https://github.com/laobamac/SimpleHDA).
Neste ambiente não foi encontrado oHAL opcional nos dois caminhos usuais
consultados. O pacoteEFI não instala plugins fora da partiçãoEFI.

A validação explícita mais recente de áudio foi música nosAirPods viaBluetooth.
Isso não é um teste do microfone/jack/alto-falantesALC257. Não atribuir esse
resultado ao áudio integrado.

## Wi-Fi

O perfil inclui AirPort_RTW89 0.4.0, revisão indicada pelo pacote`3b49703`,
para RTL8852AE/PCI 10ec:8852, junto de IO80211FamilyLegacy, IOSkywalkFamily e
AMFIPass1.4.1. A personalidadefront da kext vem depois do pacote principal.

Fonte e documentação: [FranciumOS-org/Airport_RTW89](https://github.com/FranciumOS-org/Airport_RTW89).
As dependênciasApple são as do perfil registrado no manifesto; não substituir
isoladamente por versões diferentes sem conferir a compatibilidade do conjunto.

Não foram feitos benchmarksWi-Fi, testesAirDrop/AWDL/Continuidade ou validação
de repouso nesta rodada. O upstream descreve os próprios limites e modelos testados.

## Ethernet

RealtekRTL8111 3.0.4 está incluída. O perfil não vem acompanhado de benchmark
de Ethernet ou teste de reconexão de cabo nesta validação.

## Inventário

[profiles/thinkpad-e14-gen3-amd.json](../profiles/thinkpad-e14-gen3-amd.json)
contém as versões lidas dos bundles do perfil, incluindo os plugins internos.
