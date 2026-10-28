# Histórico de mudanças verificáveis

Não há versão semântica/tag identificada. Datas de commits abaixo vêm do Git;
não indicam data de implantação no EGS. Mudanças locais não recebem data de
implementação inferida. Motivos e trade-offs: [DECISIONS](DECISIONS.md).

## 2026-10-28 — Saída do EGS ao final do cadastro

- Ao terminar normalmente, o sistema fecha a Classificação de Bobinas, clica no
  ícone desligar, confirma em **Sim** e aguarda a tela de login. O navegador
  continua aberto. Paradas por saldo, interrupções e erros mantêm a sessão.
- Falha na saída é registrada no log e não muda o resultado do cadastro.
- 92 testes aprovados, incluindo fluxo de saída simulado em Chromium local; sem EGS.

## 2026-10-28 — Navegador permanece aberto ao final do cadastro

- O Chromium não fecha mais sozinho ao terminar a classificação (fim, parada,
  interrupção ou erro). Fecha quando o operador fecha a janela, quando um novo
  cadastro começa ou quando o aplicativo é fechado, sempre na thread do cadastro.
- 89 testes aprovados; espera conferida em Chromium headless local, sem EGS.

## 2026-10-28 — NF de item único e rótulos duplicados no cadastro

- NF com um só item e peso total igual ao do romaneio agora associa todos os
  grupos a esse item; **Usar associações** fica habilitado e o cadastro roda em
  uma única etapa. Produto divergente (ex.: RECICLADO faturado como MIOLO) gera alerta.
- Corrigido o erro `Rótulo de grupo duplicado: 'MIOLO'` quando o romaneio tem as
  descrições `MIOLO` e `MIOLO // MIOLO`; grupos que colidem mantêm a descrição completa.
- 84 testes aprovados; PDFs de NF/romaneio informados conferidos localmente, sem EGS.

## 2026-10-28 — Correção de leitura do romaneio Novakraft V26654

- Corrigida a conversão de peso pt-BR no romaneio: `1.583,00` agora resulta em
  1583 kg, sem erro de conversão.
- Linhas Novakraft com `/ /` no lugar de data e turno também são importadas.
- Para esse layout, o pedido do cliente (`V26654/01`) preenche a referência do
  romaneio quando não houver número próprio no documento.
- O PDF operacional não foi versionado e nenhuma ação no EGS foi executada.

## 2026-10-16 — Confirmação do aviso de peso em cada classificação

- Aviso de peso zero tem espera de aparição, clique no OK do próprio popup e
  confirmação de fechamento; falhas identificadas deixam de ser ignoradas.
- Mensagem visível substitui dependência exclusiva de classes do modal e evita
  conflito com cópias ocultas. Demais avisos não recebem confirmação automática.
- Testes Chromium locais verificam atraso, isolamento e duas bobinas seguidas,
  além dos testes de campos/saldo/histórico: 76 aprovados; sem execução no EGS.

## 2026-10-16 — Correção de NF com valores monetários concatenados

- Leitura da quantidade deixou de depender de separadores entre preço e total,
  evitando rejeição indevida de uma linha válida do DANFE ADF.
- Quantidades malformadas continuam recusadas sem importação parcial. Dois casos
  sintéticos acrescentados; 72 testes aprovados e PDFs fornecidos conferidos
  somente para leitura, sem ações no EGS nem uso do histórico operacional.

## 2026-10-15 — Número do romaneio no histórico

- Campo de romaneio extraído do PDF e editável antes do cadastro; a interface
  exige preenchimento e envia o valor para a marca de cada sucesso confirmado.
- Histórico com coluna, busca, filtro por romaneio e edição/inclusão do número.
  Registros antigos continuam legíveis sem romaneio; a deduplicação não muda.
- Mapa opcional `romaneios` preservado nas gravações atômicas. Suíte com 70 testes
  aprovada, sem acesso ao histórico operacional nem cadastro real no EGS.

## 2026-10-15 — Gestão local do histórico

- Adicionada janela para consultar/buscar, incluir manualmente, editar e excluir
  chaves locais, com confirmação sobre o efeito na prevenção de recadastro.
- Inclusão manual só grava no controle local; não interage com o EGS. JSON inválido
  deixa de ser sobrescrito por gravações, que agora usam substituição atômica.
- Cinco testes com arquivos temporários aprovados; sem uso do histórico operacional.

## 2026-10-15 — Variantes ADF e conferência opcional de NF

- Preservada a descrição completa ADF; variantes do mesmo produto-base formam
  grupos por descrição. Sem variantes, mantém-se agrupamento de pontas por largura.
- Adicionada importação opcional DANFE ADF com sugestões revisáveis por item,
  alertas de largura/referência e integração de rótulos na interface/cadastro.
  A escolha da aba/item permanece manual no EGS e a NF não é persistida.
- Histórico local ganhou manutenção manual; total de 60 testes passou com
  navegador simulado e dados sintéticos/temporários. QA visual concluído; sem
  homologação EGS, acesso a dados operacionais ou commit automático.

## 2026-10-15 — Interface dark e pontas por largura

- Redesenhada a interface nativa com paleta grafite, indicadores, cartões de peso,
  tabela escura, busca/filtro e diálogos temáticos, inspirada no shadcn/ui.
- Pontas abaixo de 1000 separadas por produto e largura no resumo e no cadastro;
  demais larguras preservam agrupamento por produto. Escolha de aba/nota é manual.
- Falha de leitura invalida lote antigo; exportação continua integral com filtros.
- 33 testes simulados aprovados e PDF fornecido conferido sem cadastro real.
  Inspeção visual concluída após desbloqueio, com ajuste de espaçamento para
  telas baixas. Sem commit automático.

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
