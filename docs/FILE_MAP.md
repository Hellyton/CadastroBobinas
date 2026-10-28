# Mapa do código

Todos os caminhos abaixo são relativos ao repositório. Use os links para chegar
ao arquivo e pesquise o símbolo; números de linha não são mantidos como contrato.

## Aplicação

| Arquivo | Responsabilidade e símbolos principais | Funcionalidades / dependências |
| --- | --- | --- |
| [main.py](../main.py) | Entrada: instancia `App`, chama `mainloop` | interface |
| [app/tema.py](../app/tema.py) | `CORES`, `texto`, `cartao`, `botao`, `menu`, `configurar_tabela`, `numero` | paleta dark, tipografia e ttk |
| [app/componentes.py](../app/componentes.py) | `Indicador`, `Dialogo` | cartões e confirmações/avisos escuros |
| [app/janela_historico.py](../app/janela_historico.py) | `JanelaHistorico` | coluna, busca e filtro por romaneio; manutenção local; CustomTkinter, ttk |
| [app/agrupamento.py](../app/agrupamento.py) | `nome_grupo`, `agrupar_bobinas`, `produtos_com_variantes` | descrição original quando há variantes; caso contrário pontas por produto e largura < 1000 |
| [app/nota_fiscal.py](../app/nota_fiscal.py) | `ler_nota_fiscal`, `ler_numero_romaneio`, `conferir_nota`; `NotaFiscal`, `ItemNotaFiscal`, `ConferenciaNota` | leitura opcional DANFE ADF e sugestões de associação revisáveis |
| [app/interface.py](../app/interface.py) | `App`; `abrir_pdf`, `fornecedor_alterado`, `processar_pdf`, `atualizar_resumo_produtos`, `exportar_excel` | importação, conferência, XLSX; CustomTkinter, ttk, openpyxl |
| [app/interface.py](../app/interface.py) | `iniciar_cadastro`, `executar_cadastro`, `processar_eventos`, `confirmar_etapa`, `alternar_pausa`, `interromper_cadastro`, `encerrar_cadastro`, `fechar_janela` | cadastro e controle; Queue, Thread, Event |
| [app/interface.py](../app/interface.py) | `_montar_*`, `_atualizar_romaneio`, `filtrar_bobinas`, `_mostrar_mensagem`, `_fechar_confirmacao` | layout dark, filtros, estado e diálogos |
| [app/leitor_pdf.py](../app/leitor_pdf.py) | `ler_romaneio(caminho, fornecedor=None)` | tripla de retorno; pdfplumber, `FORNECEDORES` |
| [app/modelos.py](../app/modelos.py) | dataclass `Bobina`, campo opcional `descricao_original` | contrato de dados de todos os parsers e cadastro; preserva texto original ADF |
| [app/parsers.py](../app/parsers.py) | `_extrair_texto`, `FORNECEDORES`, `detectar_fornecedor` | despacho e detecção por marcadores |
| [app/parsers.py](../app/parsers.py) | `extrair_bobinas_adf` | regex ADF; Bobina, pdfplumber |
| [app/parsers.py](../app/parsers.py) | `extrair_bobinas_hp`, `MAPA_PRODUTO_HP` | papel/código HP; Bobina |
| [app/parsers.py](../app/parsers.py) | `extrair_bobinas_novakraft`, `_extrair_bobinas_novakraft_romaneio`, `_extrair_bobinas_novakraft_laudo` | dois layouts; `TOKEN_NOVAKRAFT`, `PADRAO_LINHA_LAUDO_NOVAKRAFT` |
| [app/parsers.py](../app/parsers.py) | `_interpretar_codigo_produto`, `_desduplicar_codigo`, `PADRAO_PRODUTO_NOVAKRAFT`, `MAPA_PRODUTO_NOVAKRAFT` | código nominal Novakraft |
| [app/parsers.py](../app/parsers.py) | `extrair_bobinas_cocelpa`, `_agrupar_palavras_por_linha`, `_processar_coluna_cocelpa`, `_tentar_valor_ajuste`, `PADRAO_FABRICACAO` | colunas, grupos KE e ajustes; coordenadas de palavras |
| [app/cadastro.py](../app/cadastro.py) | `CadastroBobinas.iniciar`, `_executar`, `_confirmar`, `_escolher_proximo_produto`, `_parar_por_saldo`, `_resultado` | orquestração; navegador, histórico, controle, config |
| [app/navegador.py](../app/navegador.py) | `Navegador.abrir`, `acessar`, `fazer_login`, `sair_do_sistema`, `aguardar_fechamento`, `fechar` | Chromium e login; Playwright síncrono, config |
| [app/navegador.py](../app/navegador.py) | `clicar_novo`, `preencher_bobina`, `_preencher_campos`, `_fill_verificado`, `_campos_divergentes` | campos EGS; constantes `SEL_*` |
| [app/navegador.py](../app/navegador.py) | `_aguardar_campos_calculados`, `_esperar_calculo`, `_fechar_popup_peso` | recálculo, avisos e esperas |
| [app/navegador.py](../app/navegador.py) | `ler_saldo_classificar`, `ler_quantidade_classificada`, `_parse_numero`, `salvar`, `tentar_fechar_modal`, `SalvamentoNaoConfirmado` | leitura, confirmação e recuperação |
| [app/controle.py](../app/controle.py) | `ControleCadastro`: `pausar`, `continuar`, `interromper`, `verificar`, `pausado`; `CadastroInterrompido` | sincronização cooperativa via Event |
| [app/historico.py](../app/historico.py) | `_chave`, `_ler_dados`, `_salvar_dados`, `carregar_historico`, `bobina_ja_cadastrada`, `marcar_cadastrada`, `listar_registros`, `adicionar_cadastrada`, `editar_registro`, `excluir_registro` | JSON local; chaves antigas e mapa opcional de romaneios |
| [app/logger.py](../app/logger.py) | `logger.add` na importação | Loguru, destino relativo e rotação |

## Configuração e operação

| Caminho | Uso |
| --- | --- |
| [requirements.txt](../requirements.txt) | Cinco dependências diretas, sem fixação de versões |
| [config.example.py](../config.example.py) | Modelo de configuração, sem valores de credenciais |
| `config.py` | Configuração local ignorada; não copiar valores para documentação |
| [instalar.bat](../instalar.bat) | Cria/ativa venv, instala dependências e Chromium |
| [executar.bat](../executar.bat) | Muda para a raiz, ativa venv e chama main.py |
| [.gitignore](../.gitignore) | Exclusões de segredos, dados operacionais e gerados |
| [README.md](../README.md) | Instruções do operador; anterior a esta memória |
| [botoes.txt](../botoes.txt) | Anotações de seletores e intenção de rastreio; pode divergir do código |
| `historico_cadastro.json`, `logs/` | Dados locais, caminhos relativos ao diretório de execução |
| `venv/`, `__pycache__/`, `.git/` | Ambiente/cache/metadados; não são módulos funcionais |

## Verificação e suporte

| Arquivo | Símbolos e alcance |
| --- | --- |
| [tests/test_controle_cadastro.py](../tests/test_controle_cadastro.py) | `TestControleCadastro`, 7 testes de pausa, interrupção, progresso, fechamento e confirmação |
| [tests/test_agrupamento.py](../tests/test_agrupamento.py) | `TestAgrupamentoBobinas`, 7 testes de pontas/limite, variantes e integração simulada |
| [tests/test_nota_fiscal.py](../tests/test_nota_fiscal.py) | 12 testes de parser DANFE ADF, valores concatenados, quantidades inválidas, referência, associação única e ambiguidades; dados sintéticos |
| [tests/test_interface.py](../tests/test_interface.py) | `TestInterface`, 13 testes Windows de resumo, filtros/exportação, NF, romaneio, confirmação e progresso |
| [tests/test_saldo_classificacao.py](../tests/test_saldo_classificacao.py) | `TestSaldoClassificacao`, 9 testes de saldo, salvamento e romaneio no histórico; navegador simulado |
| [tests/test_historico.py](../tests/test_historico.py) | `TestGestaoHistorico`, 11 testes de leitura, compatibilidade, romaneios e CRUD com arquivos temporários |
| [tests/test_janela_historico.py](../tests/test_janela_historico.py) | `TestJanelaHistorico`, 3 testes Windows de coluna/filtro, edição e inclusão com romaneio em arquivo temporário |
| [tests/test_parsers_adf.py](../tests/test_parsers_adf.py) | Casos sintéticos de parsing ADF e preservação da descrição original |
| [tests/test_preenchimento.py](../tests/test_preenchimento.py) | `TestPreenchimento`, 9 testes de campos, popup, falha de fechamento e verificação antes de salvar |
| [tests/test_popup_peso.py](../tests/test_popup_peso.py) | `TestPopupPesoPlaywright`, 3 testes em Chromium local: aviso atrasado, isolamento e sequência de duas bobinas |
| [teste_ambiente.py](../teste_ambiente.py) | `escolher_arquivo`, `escolher_fornecedor_manualmente`; fluxo CLI contra HTML local, sem histórico |
| [mock/mock_sistema.html](../mock/mock_sistema.html) | `abrirModal`, `mostrarPopupPeso`, `atualizarSaldo`, `SALDO_INICIAL`; DOM e cálculos simulados |
| [teste_bobina.py](../teste_bobina.py) | `main`; preenche formulário no destino de config, sem chamar salvar |
| [teste_cadastro.py](../teste_cadastro.py) | `main`; uso antigo incorreto do retorno de ler_romaneio; [KI-06](KNOWN_ISSUES.md#ki-06--script-manual-incompativel) |

Rotas HTTP internas/classes de banco: **Não identificado**. A única URL local
de teste está em `teste_ambiente.URL_TESTE`; a URL EGS vem de `config.URL`.
