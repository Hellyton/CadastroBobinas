# Histórico local e prevenção de recadastro

## Objetivo
Pular bobinas reconhecidas como cadastradas em execuções anteriores.

## Status atual
Implementado no commit inicial; não oferece garantia de unicidade no EGS.

## Fluxo de funcionamento
Carrega conjunto de chaves, filtra lista antes do agrupamento e conta ignoradas.
Após confirmação de cada salvamento, recarrega JSON, adiciona chave e regrava.
Com `usar_historico=False`, o cadastro não lê nem grava esse arquivo.

## Regras de negócio
[RN-15 a RN-17](../BUSINESS_RULES.md). Contrato, normalização e compatibilidade
legada estão centralizados em [DATABASE](../DATABASE.md).

## Arquivos relacionados
[historico.py](../../app/historico.py), [cadastro.py](../../app/cadastro.py),
[interface.py](../../app/interface.py), [.gitignore](../../.gitignore).

## Funções e classes principais
`_chave`, `carregar_historico`, `bobina_ja_cadastrada`, `marcar_cadastrada`,
`CAMINHO_HISTORICO`; chamador `CadastroBobinas._executar`.

## Entradas e saídas
Número e fornecedor → chave textual. Leitura → set. Busca → bool.
Marca → regrava objeto JSON com `cadastradas` ordenadas, sem objeto de retorno.

## Persistência de dados
`historico_cadastro.json`, relativo ao diretório de execução, ignorado pelo Git.
Não inclui nota, pesos, horários, falhas ou resultados de execução.

## Integrações
Biblioteca padrão json/os; marca depende de confirmação do EGS pelo orquestrador.

## Validações e exceções
Ausência/JSONDecodeError/OSError na leitura retorna vazio; tipos de schema
inesperados podem falhar. Gravação não captura erros. Marca legada sem fornecedor
continua sendo aceita pela busca.

## Interface do usuário
Sem editor/limpeza de histórico na UI. Ignoradas aparecem no progresso/resultado.

## Testes relacionados
`test_saldo_classificacao.py` verifica chamadas de marca após sucesso e ausência
em parada/erro usando mocks; não testa arquivo real ou normalização de chaves.

## Limitações conhecidas
Sem atomicidade/lock, risco após salvamento remoto, legado entre fornecedores,
duplicatas no mesmo lote e schema não validado. [KI-01 a KI-03 e KI-12](../KNOWN_ISSUES.md).

## Melhorias planejadas
Nenhuma aprovada identificada. Integridade, recuperação e identidade precisam
de critérios no [ROADMAP](../ROADMAP.md).
