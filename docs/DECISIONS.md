# Decisões observáveis

Não foram encontrados ADRs ou registros de discussões anteriores. Quando o
motivo está num comentário, isso é indicado; fora disso, **motivo original e
alternativas consideradas: Não identificado**. Consequências abaixo derivam da
implementação e não atribuem intenção histórica aos autores.

## D-01 — Aplicação desktop modular Python

- Problema observável: importar dados e conduzir cadastro no EGS pelo operador.
- Escolha: CustomTkinter/ttk para UI, módulos separados, Playwright síncrono para navegador.
- Evidência: commit inicial `395dcaa`, [main.py](../main.py), [requirements](../requirements.txt).
- Motivo/alternativas: Não identificado; não houve comparação de frameworks recuperável.
- Consequências: ambiente Python + Chromium e dependência do DOM; sem backend próprio.

## D-02 — Cadastro em thread e mensagens para UI

- Problema: preservar resposta da janela durante cadastro e respeitar afinidade de thread.
- Escolha: `Thread`, `Queue`, `Event`; navegador nasce/trabalha/fecha na mesma thread;
  widgets pertencem à thread principal.
- Motivo evidenciado: comentários explícitos em `iniciar` e `executar_cadastro`.
- Evidência: [cadastro.py](../app/cadastro.py), [interface.py](../app/interface.py),
  [controle.py](../app/controle.py), commit `395dcaa`.
- Consequências: pausa/interrupção cooperativas e espera por operação em andamento;
  alternativas consideradas não identificadas. Extração de PDF continua síncrona.

## D-03 — Histórico por fornecedor e número, com legado

- Problema: fornecedores diferentes podem usar mesmo número de bobina.
- Escolha: chave composta e fallback para número puro; JSON local gravado a cada sucesso.
- Motivo evidenciado: docstrings de `_chave` e `bobina_ja_cadastrada`.
- Evidência: [historico.py](../app/historico.py), já presente em `395dcaa`.
- Consequências: preserva entradas antigas, porém chave legada pode ignorar fornecedor;
  gravação não é transacional. A mudança anterior de formato é descrita em comentários,
  mas sua data/commit/discussão anteriores ao repositório não foram recuperados.

## D-04 — Extração Cocelpa por coordenadas e grupos

- Problema: duas colunas de bobinas e marcador KE posterior à primeira linha.
- Escolha: `extract_words`, divisão por metade da página, agrupamento antes de criar bobinas.
- Motivo evidenciado: comentários/docstring explicam ambiguidade do texto puro e
  necessidade de aplicar KE inclusive à primeira bobina.
- Evidência: [parsers.py](../app/parsers.py): `extrair_bobinas_cocelpa`,
  `_processar_coluna_cocelpa`, commit `395dcaa`.
- Consequências: depende das coordenadas e de reinício de grupo por coluna/página;
  alternativa citada: texto puro, com ambiguidade descrita. Outras alternativas não identificadas.

## D-05 — Robustez específica Novakraft

- Problema descrito em comentários: quebras de linha ausentes e código com caracteres duplicados.
- Escolha: tokens no texto do romaneio, normalização de pares e ramo separado de laudo.
- Evidência: `TOKEN_NOVAKRAFT`, `_desduplicar_codigo`, `extrair_bobinas_novakraft`
  em [parsers.py](../app/parsers.py), commit `395dcaa`.
- Consequências: tolera esses padrões e ignora ensaios do laudo; não implementa OCR.
  Comentários sobre PDFs escaneados não comprovam OCR; justificativa completa,
  alternativas e datas anteriores ao commit inicial não foram recuperadas.

## D-06 — Saldo como pré-condição e evidência de salvamento

- Problema: peso pode ultrapassar saldo; fechamento do modal sozinho não prova gravação.
- Escolha: validar antes de cada bobina e aceitar sucesso só após saldo esperado;
  confirmação incerta interrompe sem histórico.
- Evidência: commit `3dbea63` de 2026-10-07; [salvar](../app/navegador.py),
  [_executar](../app/cadastro.py), [test_saldo_classificacao](../tests/test_saldo_classificacao.py).
- Motivo: mensagem do commit, comentários e testes sustentam essa proteção; detalhes
  da discussão e alternativas não identificados.
- Consequências: exige conferência manual em timeout; não cria transação entre EGS e JSON.
  Modifica o comportamento inicial que aguardava apenas remoção do modal.

## D-07 — Verificação de campos e resumo por produto no checkout

- Problemas evidenciados: campos podem ser apagados por avisos/recálculos; operador
  precisa visualizar quantidade e peso por produto.
- Escolha atual: campos visíveis, nova conferência/repetição após cálculo e antes
  de salvar, fechamento seletivo do aviso; tabela de totais por produto sem ajuste.
- Evidência: diffs locais de [navegador.py](../app/navegador.py),
  [interface.py](../app/interface.py), README e teste local
  [test_preenchimento.py](../tests/test_preenchimento.py).
- Consequências: limite de tentativas; resumo usa lista integral. Os testes
  sustentam cenários simulados, sem homologação no EGS.
- Datas de implementação, commits, alternativas e aprovação originais: Não identificado.
  São mudanças preexistentes preservadas, não implementações desta tarefa.

## D-08 — Memória técnica modular

- Problema: continuidade entre conversas e custo de recuperar contexto.
- Escolha solicitada nesta tarefa: AGENTS como roteador, índice, documentos temáticos,
  regras com IDs e um arquivo por funcionalidade.
- Motivo: consulta progressiva, evidência rastreável e manutenção localizada,
  conforme solicitação do usuário em 2026-10-15.
- Consequências: documentação precisa acompanhar mudanças; código continua referência.
  Não foram alterados código, dados ou regras; não houve commit automático.


## D-09 — Redesenho escuro mantendo o aplicativo desktop

- Solicitação em 2026-10-15: interface dark, bonita e simples, inspirada em Shadow UI.
- Referência visual adotada: [shadcn/ui](https://ui.shadcn.com/docs/theming), com
  superfícies grafite, bordas discretas e hierarquia de ações; implementação nativa
  em CustomTkinter/ttk, sem migrar para React ou adicionar dependências.
- Paleta/componentes separados em `app/tema.py` e `app/componentes.py`.
  Busca/filtro são visuais; resumo, exportação e cadastro usam a lista integral.
- Confirmações em diálogo escuro com interrupção explícita; Queue/Thread/Event
  e confirmação de salvamento permanecem no fluxo existente.

## D-10 — Pontas separadas por largura

- Regra confirmada pelo usuário: abaixo de 1000 é ponta e cada largura corresponde
  a uma aba de classificação. Produto permanece na chave para não misturar papéis.
- Helper `app/agrupamento.py` compartilhado entre interface e cadastro evita
  divergência entre peso exibido e lote processado. Largura 1000 não é ponta.
- Não lê item NF nem seleciona abas automaticamente; operador confere a aba/nota.

## D-11 — Descrição original como contexto de agrupamento

- Problema: produtos-base iguais podem representar descrições de classificação
  distintas no documento de origem.
- Escolha: preservar a descrição completa do ADF e, havendo variantes do mesmo
  produto-base, agrupar por descrição antes do filtro de histórico e independente
  da largura. Sem variantes, permanece o fallback de ponta por largura < 1000.
- Evidência: [Bobina](../app/modelos.py), [parser ADF](../app/parsers.py),
  [agrupamento](../app/agrupamento.py), testes sintéticos de parser/agrupamento.
- Consequências: texto original não altera o produto-base nem o peso; grupos
  remanescentes mantêm contexto após o filtro do histórico.

## D-12 — Conferência de NF opcional com revisão humana

- Problema: relacionar grupos do romaneio a itens impressos na nota sem misturar
  linhas repetidas nem escolher ambiguidades automaticamente.
- Escolha: leitura opcional DANFE ADF; sugerir somente correspondência única por
  produto e peso exato, alertar divergência de largura e bloquear referência
  incompatível. Operador confirma associação e continua selecionando no EGS.
- Evidência: [nota_fiscal.py](../app/nota_fiscal.py), [interface.py](../app/interface.py),
  testes sintéticos de NF/interface e [CONFERENCIA_NF](features/CONFERENCIA_NF.md).
- Consequências: parser limitado ao layout textual DANFE ADF e unidade KG; a NF
  não é persistida e a confirmação não comprova a classificação remota.

## D-13 — Romaneio como metadado do histórico

- Solicitação: guardar o número do romaneio para facilitar filtros.
- Escolha: preservar `cadastradas` e a identidade fornecedor/bobina, acrescentando
  mapa opcional `romaneios` por chave. Arquivos antigos seguem válidos sem inferir
  a origem de registros; edição permite completar o campo.
- A interface obtém o número do PDF quando reconhecido e permite correção manual.
  Captura-o antes do worker, gravando somente após confirmação de salvamento.
- Evidência: [historico.py](../app/historico.py), [interface.py](../app/interface.py),
  [janela_historico.py](../app/janela_historico.py) e testes temporários/simulados.
- Consequência: romaneio organiza a consulta; não autoriza recadastro da mesma
  bobina. Corrigir o campo invalida as associações anteriores da NF.

## D-14 — NF de item único define a divisão do cadastro

- Solicitação: quando a NF tem um só item, o sistema deve se adaptar à NF em vez
  de bloquear por divergência entre os grupos do romaneio e o produto faturado.
- Escolha: com item único e peso total do romaneio igual ao peso do item, todos
  os grupos são associados a ele e o cadastro roda em uma única etapa (sem troca
  de produto). Produto ou largura divergente vira alerta; referência de romaneio
  divergente continua bloqueando; peso total diferente mantém a regra anterior.
- Evidência: [nota_fiscal.py](../app/nota_fiscal.py) `conferir_nota`,
  [cadastro.py](../app/cadastro.py) `grupo_unico`, [interface.py](../app/interface.py)
  `_grupo_unico_nf` e testes sintéticos de NF, cadastro e interface.
- Consequência: a separação por produto deixa de existir no EGS para essas NFs;
  o operador seleciona uma única nota/aba antes de iniciar.
