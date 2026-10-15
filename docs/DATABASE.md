# Banco de dados e persistência

## Tecnologia e fronteira

Não há banco de dados próprio, SQL, ORM, tabelas, migrações ou API de persistência
identificados. A persistência local é um arquivo JSON e logs; XLSX é uma exportação.
O banco, as tabelas e a transação interna do EGS: **Não identificado**.

## Modelo em memória

Fonte: [modelos.Bobina](../app/modelos.py). As anotações da dataclass não fazem
validação de tipo/intervalo em tempo de execução.

| Campo | Tipo declarado | Origem / significado verificável |
| --- | --- | --- |
| `numero` | str | Identificador extraído; preservado no campo Observação do EGS |
| `produto` | str | Texto do PDF ou mapeamento do parser |
| `gramatura` | int | Valor nominal extraído para preencher o EGS |
| `formato` | int | Dimensão extraída; HP usa Largura |
| `diametro` | int | Dimensão extraída |
| `peso` | int | Peso em kg; conversão/arredondamento depende do parser |
| `rua` | int, padrão 1 | Enviado ao EGS e à planilha; config.RUA_PADRAO não é consultado |
| `fornecedor` | str, padrão vazio | Atribuído por App.processar_pdf e teste_ambiente; leitor retorna separadamente |

Não há PK/FK, índices, restrições declarativas ou relacionamentos persistidos
entre bobina, nota e produto. O agrupamento por produto é transitório.

## Histórico JSON

Fonte: [historico.py](../app/historico.py). `CAMINHO_HISTORICO` aponta para
`historico_cadastro.json`, relativo ao diretório de execução.
Contrato lógico: objeto com propriedade `cadastradas`, lista de strings.
Chave nova: `FORNECEDOR_NORMALIZADO|numero`; fornecedor usa `strip().upper()`.
Sem fornecedor, usa `str(numero)`. O número não recebe strip ou normalização
numérica. Não há registro de nota, peso, horário, tentativa ou status de falha.

| Operação | Comportamento |
| --- | --- |
| `carregar_historico` | Lê JSON e retorna set; inexistência, JSON inválido ou OSError retornam set vazio |
| `bobina_ja_cadastrada` | Busca chave composta e, depois, número puro para reconhecer legado |
| `marcar_cadastrada` | Recarrega arquivo, adiciona chave, ordena set e regrava JSON UTF-8 completo |
| `CadastroBobinas._executar` | Lê histórico uma vez para filtrar o lote; marca cada sucesso confirmado |
| `usar_historico=False` | Não lê/grava histórico no fluxo de cadastro; usado no simulador |

Compatibilidade com entradas antigas é uma consulta alternativa, não uma
migração executada. Não existe versão de schema nem ferramenta de migração.
Tipos de JSON inesperados não são integralmente tratados pelo carregador.

## Integridade e recuperação

- A marca local ocorre depois da confirmação de saldo do EGS; falha de disco
  nesse intervalo pode deixar cadastro remoto sem marca local.
- Gravação direta, sem arquivo temporário/replace, lock ou transação: várias
  instâncias podem sobrescrever alterações. Deduplicação não é garantia remota.
- Histórico ilegível é tratado como vazio; ausência da chave local não prova
  ausência de cadastro no EGS. Entrada legada sem fornecedor vale para todos.
- Duplicatas dentro do PDF não são removidas após o filtro inicial.
- Preserve o histórico operacional ao transferir máquinas; não o versione nem
  o edite para presumir sucesso. Após falha, confronte a situação no EGS.

Riscos com evidências: [KI-01 a KI-03 e KI-12](KNOWN_ISSUES.md).
Regras: [RN-15 a RN-17](BUSINESS_RULES.md). Nenhum dado operacional real foi
copiado para esta documentação e nenhuma migração foi executada.

## Outros arquivos

`logs/cadastro.log` é adicionado na importação de `app.logger`, com rotação de
1 MB e UTF-8. Não há retenção máxima configurada. XLSX é criado no caminho
escolhido, com uma aba de bobinas; não é utilizado como entrada nem histórico.
Backups automáticos e política institucional de retenção: **Não identificado**.
