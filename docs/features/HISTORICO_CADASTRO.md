# Histórico local e prevenção de recadastro

## Objetivo
Pular bobinas reconhecidas como cadastradas em execuções anteriores.

## Status atual
Consulta, inclusão manual, edição e exclusão locais estão disponíveis na janela
Histórico. O filtro pode restringir por número exato de romaneio ou por registros
sem romaneio. A inclusão manual só marca o controle local e não cadastra no EGS.
Essas ações alteram a prevenção de recadastro, não oferecem garantia de unicidade
no EGS.

## Fluxo de funcionamento
Carrega conjunto de chaves, filtra lista antes do agrupamento e conta ignoradas.
Após confirmação de cada salvamento, recarrega JSON, adiciona chave e, quando
informado, associa o romaneio ao registro; só então regrava.
Com `usar_historico=False`, o cadastro não lê nem grava esse arquivo.
Na interface, o número do romaneio pode ser extraído do PDF carregado ou corrigido
manualmente e é exigido antes de iniciar o cadastro. O valor é capturado antes
do worker e só gravado após salvamento confirmado. A janela permite buscar por
fornecedor/número/romaneio, filtrar por todos, número exato ou sem romaneio,
incluir, editar e excluir registros. Inclusão/edição aceitam o romaneio antigo;
None preserva o metadado em chamadas da API e string vazia o limpa. A edição
troca a identidade usada na prevenção se fornecedor/número mudar; o romaneio
não altera a identidade. A exclusão pode permitir recadastro. O botão fica
desabilitado durante o cadastro e uma janela aberta é fechada antes da execução.

## Regras de negócio
[RN-15 a RN-17](../BUSINESS_RULES.md). Contrato, normalização e compatibilidade
legada estão centralizados em [DATABASE](../DATABASE.md).

## Arquivos relacionados
[historico.py](../../app/historico.py), [cadastro.py](../../app/cadastro.py),
[interface.py](../../app/interface.py), [.gitignore](../../.gitignore).

## Funções e classes principais
`_chave`, `carregar_historico`, `bobina_ja_cadastrada`, `marcar_cadastrada`,
`listar_registros`, `adicionar_cadastrada`, `editar_registro`, `excluir_registro`,
`CAMINHO_HISTORICO`; `JanelaHistorico`; chamador `CadastroBobinas._executar`.

## Entradas e saídas
Fornecedor e número → chave textual. O mapa opcional relaciona essa chave ao
romaneio. Leitura para o cadastro → set; `listar_registros` inclui o campo
`romaneio`. Busca → bool. O parâmetro opcional `romaneio` em `marcar_cadastrada`
e nos métodos de inclusão/edição atualiza metadado sem mudar a chave.

## Persistência de dados
`historico_cadastro.json`, relativo ao diretório de execução, ignorado pelo Git.
Mantém `cadastradas` (lista de chaves) e `romaneios` (mapa opcional chave →
número). JSON legado sem mapa é lido com romaneio vazio; registros antigos não
são inferidos automaticamente. Não inclui NF, pesos, horários, falhas ou
resultados de execução.

## Integrações
Biblioteca padrão json/os; marca depende de confirmação do EGS pelo orquestrador.

## Validações e exceções
Ausência retorna vazio. `carregar_historico` mantém o retorno `set` vazio para
JSON malformado, schema inválido ou erro de leitura por compatibilidade; a leitura
estrita exige raiz objeto, `cadastradas` como lista de strings não vazias e valida
o mapa `romaneios` quando presente. Marcação e gestão falham sem substituir
arquivo inválido. Escritas usam arquivo temporário
e `os.replace`. Chaves legadas sem fornecedor continuam reconhecidas. Inclusão e
edição manuais removem só espaços externos do número, preservam zeros/letras/espaços
internos e rejeitam `|` no fornecedor. Duplicatas já reconhecidas são recusadas.

## Interface do usuário
Busca, filtro por romaneio, adição manual, edição e exclusão são feitas na janela
Histórico. O formulário de inclusão/edição aceita o número do romaneio; filtro
disponibiliza **Todos**, número exato e **Sem romaneio**. Não há ação de limpar
tudo. Confirmações explicam que a inclusão manual não interage com o EGS, e que
editar/excluir altera a prevenção local de recadastro.

## Testes relacionados
`test_saldo_classificacao.py` verifica chamadas de marca após sucesso e ausência
em parada/erro usando mocks; `test_historico.py` cobre schema legado/novo,
preservação e limpeza do metadado, CRUD e falhas em arquivo temporário.
`test_janela_historico.py` cobre filtro e edição visualmente isolados. QA visual
passou com JSON fictício; nenhum histórico operacional foi lido.

## Limitações conhecidas
Sem lock; cadastro e editor são serializados pela interface. Registros antigos
sem metadado continuam sem número de romaneio até atualização manual. Persiste o risco após
salvamento remoto, legado entre fornecedores e duplicatas no mesmo lote. A leitura
de cadastro inválida continua retornando vazio por compatibilidade, portanto não
prova ausência de cadastro remoto. [KI-01 a KI-03 e KI-12](../KNOWN_ISSUES.md).

## Melhorias planejadas
Não há limpeza em massa. Integridade, recuperação e identidade remota continuam
com os limites descritos no [ROADMAP](../ROADMAP.md).
