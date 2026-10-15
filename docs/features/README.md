# Índice de funcionalidades

**12 funcionalidades documentadas.** Todos os status abaixo se referem à
implementação observada; testes simulados não representam homologação no EGS.
Leia somente o documento relacionado à tarefa, depois confirme seu símbolo no código.

| Funcionalidade | Documento | Entrada de código / status |
| --- | --- | --- |
| Importação e escolha de fornecedor | [IMPORTACAO_ROMANEIOS](IMPORTACAO_ROMANEIOS.md) | `ler_romaneio`, `App.processar_pdf`; implementada |
| Layout ADF | [PARSER_ADF](PARSER_ADF.md) | `extrair_bobinas_adf`; implementado |
| Layout HP | [PARSER_HP](PARSER_HP.md) | `extrair_bobinas_hp`; implementado |
| Novakraft: romaneio e laudo | [PARSER_NOVAKRAFT](PARSER_NOVAKRAFT.md) | `extrair_bobinas_novakraft`; implementado |
| Cocelpa: colunas, KE e ajustes | [PARSER_COCELPA](PARSER_COCELPA.md) | `extrair_bobinas_cocelpa`; implementado |
| Conferência e resumo por produto | [CONFERENCIA_RESUMO](CONFERENCIA_RESUMO.md) | `App.atualizar_resumo_produtos`; implementada, resumo em diff local |
| Exportação XLSX | [EXPORTACAO_EXCEL](EXPORTACAO_EXCEL.md) | `App.exportar_excel`; implementada |
| Cadastro de lotes/produtos | [CADASTRO_LOTES](CADASTRO_LOTES.md) | `CadastroBobinas.iniciar`; implementado, testes simulados |
| Preenchimento e confirmação EGS | [PREENCHIMENTO_EGS](PREENCHIMENTO_EGS.md) | `Navegador`; implementado, melhorias em diff local e testes simulados |
| Histórico e prevenção de recadastro | [HISTORICO_CADASTRO](HISTORICO_CADASTRO.md) | `app.historico`; implementado, limites de integridade |
| Controle de execução desktop | [CONTROLE_EXECUCAO](CONTROLE_EXECUCAO.md) | `ControleCadastro`, `App.processar_eventos`; implementado, testes simulados |
| Ambiente simulado local | [SIMULADOR_LOCAL](SIMULADOR_LOCAL.md) | `teste_ambiente.py` + HTML; implementado, não executado nesta tarefa |

Regras centralizadas: [BUSINESS_RULES](../BUSINESS_RULES.md). Símbolos/caminhos:
[FILE_MAP](../FILE_MAP.md). Pendências não aprovadas: [ROADMAP](../ROADMAP.md).
Cada funcionalidade mantém o modelo de 14 seções solicitado; assuntos comuns
são referenciados para evitar repetir regras e detalhes de infraestrutura.
