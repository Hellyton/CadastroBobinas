# Histórico de mudanças verificáveis

Não há versão semântica/tag identificada. Datas de commits abaixo vêm do Git;
não indicam data de implantação no EGS. Mudanças locais não recebem data de
implementação inferida. Motivos e trade-offs: [DECISIONS](DECISIONS.md).

## 2026-10-15 — Resumo por produto, preenchimento verificado e documentação

- Versionadas as alterações preexistentes de resumo de quantidade/peso por produto
  e organização dos controles na janela.
- Versionadas as proteções de preenchimento: recuperação de campos apagados,
  conferência após recálculo e antes de salvar, popup seletivo e menos esperas fixas.
- Incluídos 8 testes de preenchimento, AGENTS e documentação modular do projeto.
- Suíte de 23 testes aprovada com navegador simulado; sem homologação no EGS.
- Commit e publicação em repositório privado solicitados explicitamente pelo usuário.

## 2026-10-15 — Documentação desta tarefa, sem commit

- Criados AGENTS e documentação modular em docs, incluindo 12 funcionalidades,
  regras verificadas, mapa de símbolos, persistência e limitações.
- Analisados os dois commits, o checkout e alterações locais anteriores.
- 23 testes unitários passaram no venv existente com navegador simulado e logs
  temporários. Python global não tinha Playwright.
- Código/arquivos operacionais e mudanças anteriores foram preservados;
  sem migrações, instalação de dependências ou commit automático.

## Alterações locais preexistentes — Observadas em 2026-10-15

**Data de implementação e commit: Não identificado.**

- `app/interface.py`: resumo de quantidade/peso por produto e disposição dos controles.
- `README.md`: instruções sobre resumo por produto e ajuste apenas no total geral.
- `app/navegador.py`: preenchimento de campos visíveis, recuperação de valores
  apagados, verificação após recálculo/antes de salvar e popup de peso seletivo;
  redução de esperas fixas no caminho normal.
- `tests/test_preenchimento.py`: 8 testes de regressão, não rastreado no início da análise.

## 2026-10-07 — `3dbea63`

Mensagem: **Valida saldo da nota e confirma salvamento das bobinas**.

- Verificação de saldo antes de cada bobina e parada com motivo.
- `SalvamentoNaoConfirmado`: sucesso exige formulário removido e saldo esperado.
- Histórico não recebe marca de salvamento incerto; lote para para conferência.
- Interface mostra motivo/parada e quantidade não processada.
- Adicionados 8 testes de saldo e ajustados testes de controle/README.

## 2026-10-01 — `395dcaa`

Mensagem: **Versão inicial com cadastro em segundo plano e controles de execução**.

- Primeiro snapshot disponível: UI desktop, quatro parsers, laudo Novakraft,
  exportação XLSX, agrupamento por produto, login/cadastro EGS e histórico composto.
- Cadastro em thread, pausa/continuação/interrupção, progresso e confirmações.
- Scripts Windows, configuração de exemplo, logs, simulador local e 7 testes de controle.

O commit inicial já reúne essas funcionalidades; não é possível atribuir-lhes
datas individuais, ordem de desenvolvimento ou decisões anteriores a esse snapshot.
