# Estado atual para retomada

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
