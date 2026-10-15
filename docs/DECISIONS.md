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
