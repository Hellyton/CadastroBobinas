# Memória técnica do projeto

Base analisada em **2026-10-15**: checkout `main`, HEAD `3dbea63`, incluindo
alterações locais já existentes. Esta documentação orienta consultas; confirme o
comportamento no código antes de editar. Entrada permanente: [AGENTS.md](../AGENTS.md).

## Consulta progressiva

| Tarefa | Documento inicial | Aprofundamento |
| --- | --- | --- |
| Retomar uma conversa | [Estado atual](CURRENT_STATE.md) | [Funcionalidade](features/README.md) e código |
| Entender finalidade | [Visão geral](PROJECT_OVERVIEW.md) | [Glossário](GLOSSARY.md) |
| Localizar implementação | [Mapa do código](FILE_MAP.md) | Símbolo indicado no arquivo |
| Entender fluxo e threads | [Arquitetura](ARCHITECTURE.md) | [Controle de execução](features/CONTROLE_EXECUCAO.md) |
| Alterar regra ou parser | [Regras](BUSINESS_RULES.md) | [Funcionalidade](features/README.md) pertinente |
| Investigar dados locais | [Persistência](DATABASE.md) | [Histórico](features/HISTORICO_CADASTRO.md) |
| Investigar EGS/arquivos | [Integrações](API_INTEGRATIONS.md) | [Preenchimento](features/PREENCHIMENTO_EGS.md) |
| Executar e testar | [Guia de desenvolvimento](DEVELOPMENT_GUIDE.md) | [Simulador](features/SIMULADOR_LOCAL.md) |
| Consultar justificativa | [Decisões](DECISIONS.md) | [Histórico de mudanças](CHANGELOG.md) |
| Priorizar pendências | [Roadmap](ROADMAP.md) | [Problemas conhecidos](KNOWN_ISSUES.md) |

## Evidências e limites

- **Implementado:** constatado em fonte; não implica homologação no EGS.
- **Verificado por teste:** cobertura descrita com seu alcance e resultado.
- **Observado no checkout:** alteração local sem data de implementação ou commit atribuível.
- **Proposto / pendente de confirmação:** registro ou sugestão sem aprovação identificada.
- **Não identificado:** evidência ausente nos arquivos e dois commits disponíveis.

Foram inspecionados todos os arquivos de fonte/configuração de exemplo, testes,
scripts, simulador, README e anotações versionados, além do teste local não rastreado.
`venv`, caches e `.git` foram tratados como infraestrutura, não fonte funcional.
Conteúdo de credenciais, histórico operacional e logs não foi transcrito nem usado
como requisito. Não foram consultados serviços externos, PDFs operacionais ou
conversas anteriores. Não há release/tag nem histórico anterior ao commit inicial.

## Manutenção incremental

Ao mudar uma funcionalidade, atualize seu arquivo e somente as referências afetadas.
Regras têm IDs estáveis em BUSINESS_RULES; problemas em KNOWN_ISSUES; decisões em
DECISIONS. Os arquivos de funcionalidades remetem a essas fontes para evitar cópias.
Registre evidência (caminho + símbolo, commit ou teste), status e limitações; não
atribua datas/justificativas sem fonte. CHANGELOG registra a mudança; CURRENT_STATE
resume o necessário para retomar. Não transforme sugestões em requisitos aprovados.

Valide links, caminhos, títulos do modelo de funcionalidade e ausência de segredos
após alterações documentais. Evite uma auditoria completa a cada manutenção.

## Validação da entrega inicial da documentação

Em 2026-10-15: 28 arquivos Markdown, 12 funcionalidades, 325 links locais e 19
âncoras conferidos; estrutura obrigatória e 14 seções de cada funcionalidade
validadas. SHA-256 confirmou preservação de 26 arquivos preexistentes, incluindo
fontes, testes locais, configuração e histórico. A verificação de credenciais
locais e padrões de segredos não encontrou exposição nos documentos. Resultado
da suíte e limitações de homologação estão no [guia](DEVELOPMENT_GUIDE.md).

O índice atual contém 13 funcionalidades, incluindo a conferência opcional de NF.
As alterações posteriores e suas verificações estão no [estado atual](CURRENT_STATE.md)
e no [histórico de mudanças](CHANGELOG.md).
