# Estado atual para retomada

## Atualização — confirmação do aviso de peso, 2026-10-16

- Corrigida a verificação instantânea do popup que podia perder sua abertura.
  A cada bobina, após Rua/Diâmetro/Formato e clique em Peso, aguarda o aviso,
  confirma o OK correspondente e aguarda fechamento antes de preencher Peso.
- Localização usa mensagem visível e botão OK do mesmo popup, incluindo cópias
  ocultas do texto; falha ao fechar um aviso identificado gera erro explícito.
  As esperas de aparição, clique e fechamento têm limite de 3 s por etapa.
- Regressão em Chromium local confirmou duas bobinas, ordem dos eventos e
  preservação dos primeiros campos. Suíte de 76 testes aprovada, sem acesso EGS.
- Reabrir o aplicativo e validar no uso real; seletores do EGS continuam sujeitos
  ao DOM real conforme [PREENCHIMENTO_EGS](features/PREENCHIMENTO_EGS.md).

## Atualização — leitura de NF com colunas concatenadas, 2026-10-16

- Corrigido o falso erro de último item incompleto quando a extração textual
  junta preço unitário e valor total. A leitura usa os campos até a quantidade KG,
  sem depender das colunas monetárias, e valida o token numérico completo.
- Mantidas rejeições de unidade/quantidade inválida e importação parcial, além
  das regras de associação por produto/peso e revisão da referência.
- Verificação: 72 testes aprovados; leitura direta da NF informada e regressão
  com NF anterior conferidas, sem cadastro no EGS ou alteração do histórico.
- Reabrir o aplicativo e repetir a importação. Layouts diferentes seguem
  sujeitos ao suporte textual documentado em [CONFERENCIA_NF](features/CONFERENCIA_NF.md).

## Atualização — romaneio no histórico, 2026-10-15

- Novos cadastros da interface exigem o número do romaneio, extraído do PDF
  quando reconhecido ou informado/corrigido no campo ao lado do fornecedor.
  O valor é capturado antes do worker e gravado somente após salvar com confirmação.
- Histórico mostra coluna, busca e filtro exato por romaneio; inclusão manual
  exige o número e edição permite completar registros antigos. Legados ficam
  sem romaneio, sem inferência ou alteração do histórico operacional nesta tarefa.
- JSON mantém `cadastradas` e acrescenta mapa opcional `romaneios`; a identidade
  continua fornecedor/bobina. Alterar o número na interface descarta a conferência
  NF anterior para exigir nova revisão da referência.
- Verificação: 70 testes aprovados com dados sintéticos/temporários e EGS simulado.
  Conferência visual do campo e do filtro por romaneio concluída com JSON fictício.
  Reabrir o aplicativo para usar o campo; não houve cadastro real no EGS.

## Atualização — variantes ADF e conferência opcional de NF, 2026-10-15

- A descrição original ADF é preservada sem alterar o produto-base. Produtos com
  descrições distintas agrupam por descrição, mesmo com larguras diferentes;
  contexto é calculado antes do filtro do histórico. Sem variantes, pontas
  (< 1000) agrupam por produto e largura; >= 1000 por produto.
- Importação opcional de DANFE ADF apresenta sugestões por produto/peso exato
  único, com alertas/pendências para revisão. Referência divergente bloqueia
  sugestões; operador confirma e seleciona manualmente a aba/item no EGS.
- Interface de histórico CRUD local-only implementada. Suíte: 60/60 testes,
  com navegador simulado e dados sintéticos/temporários; QA visual da interface,
  conferência NF e CRUD concluído. Sem cadastro EGS ou alteração de dados reais.
- Próxima etapa: operador pode validar o fluxo no uso real; nenhuma ação no EGS
  foi homologada. Consultar [índice](features/README.md) e [regras](BUSINESS_RULES.md).

## Atualização — gestão local do histórico, 2026-10-15

- Incluída janela modal para buscar, adicionar manualmente, editar e excluir chaves
  locais; a confirmação deixa claro que inclusão manual não opera o EGS e que
  edição/exclusão altera a prevenção de recadastro.
- Gravações administrativas e marcação de sucesso usam JSON temporário e troca
  atômica; JSON inválido não é substituído por um histórico vazio. O carregador
  mantém seu contrato de retorno `set` para compatibilidade.
- Cinco testes focados passaram com arquivos temporários; nenhuma leitura ou
  alteração do histórico operacional foi feita. Revisão visual do CRUD ainda
  pendente nesta tarefa.

## Atualização — interface e pontas, 2026-10-15

- Redesenho dark nativo em `app/interface.py`, `app/tema.py` e `app/componentes.py`:
  indicadores, tabela escura, busca/filtro, resumo lateral e diálogos temáticos.
- `app/agrupamento.py` compartilhado por interface/cadastro: variantes de descrição
  agrupam por descrição completa; sem variantes, largura < 1000 agrupa por produto
  e largura e >= 1000 mantém produto. Escolha da aba/nota continua manual.
- Estado posterior atualiza testes e escopo na seção mais recente acima.
- Conferência visual concluída após desbloqueio: janela carregada/vazia, largura
  mínima, filtro, rolagem dos pesos e diálogo de classificação com dados fictícios.
  Ajustado modo compacto para telas baixas, ampliando a tabela de 137 para 221 px
  na tela verificada. Os 33 testes passaram novamente.
- Próximo passo: operador reabrir `executar.bat` para usar a nova interface.
  Seleção de nota/salvamento no EGS não foi homologada.

## Registro anterior à alteração acima

Referência em **2026-10-15**: branch `main`; novo commit solicitado sobre `3dbea63`,
sem tag/versão identificada. Código é a referência; documentação cobre o checkout.

- **Implementado:** quatro fornecedores, dois layouts Novakraft, conferência,
  exportação, cadastro por produto, histórico e controles de execução.
  [Índice de funcionalidades](features/README.md).
- **Base anterior:** `3dbea63`, saldo preventivo e confirmação de salvar pelo saldo.
- **Entrega solicitada:** versionar resumo por produto, proteção de preenchimento,
  testes e documentação; publicar em novo repositório privado no GitHub.
- **Mudanças locais anteriores preservadas:** README, `app/interface.py`,
  `app/navegador.py` e `tests/test_preenchimento.py` não rastreado; resumo por produto
  e proteção contra campos apagados. Inclusão no novo commit autorizada em 2026-10-15.
- **Esta tarefa concluída:** AGENTS e memória modular criados; nenhuma mudança
  de comportamento, dados ou migração durante a criação da memória.
  Posteriormente, o usuário autorizou commit e publicação no GitHub.
- **Verificação:** 23 testes existentes passaram no venv (Python 3.10.9), com
  navegador simulado e logs temporários. Python global não tinha Playwright.
  Homologação no EGS, PDFs reais e teste visual: não realizados.
- **Trabalho em andamento identificável:** apenas os diffs locais acima;
  responsável, próxima entrega e status de revisão: Não identificado.
- **Limitações relevantes:** histórico não transacional/sem deduplicar lote,
  conferência global entre notas, diferenças numéricas de parsers,
  `teste_cadastro.py` incompatível e configurações não aplicadas.
  [KNOWN_ISSUES](KNOWN_ISSUES.md) contém evidências.
- **Próximo passo verificável:** consultar `git status --short`, identificar a
  funcionalidade pedida e confirmar símbolo no [FILE_MAP](FILE_MAP.md).
  Para correções futuras, definir prioridade/aceite das [pendências](ROADMAP.md)
  e escolher teste apropriado no [guia](DEVELOPMENT_GUIDE.md).

Não há implementação adicional aprovada nesta tarefa. A publicação no GitHub
foi solicitada; verificar `git remote -v` e o estado do envio para retomar. Histórico de discussões,
releases e decisões anteriores ao primeiro commit não foi recuperado;
[DECISIONS](DECISIONS.md) registra os limites da evidência.
