# Glossário

Definições limitadas ao uso no código; não substituem uma especificação industrial.

| Termo | Significado verificado | Fonte |
| --- | --- | --- |
| Bobina | Objeto com número, produto, gramatura, formato, diâmetro, peso, rua e fornecedor | [modelos.py](../app/modelos.py) |
| Romaneio | PDF de entrada que contém registros para extração; layouts por fornecedor | [leitor_pdf.py](../app/leitor_pdf.py) |
| Fornecedor | Chave de parser: ADF, HP, Novakraft ou Cocelpa; compõe histórico | [parsers.py](../app/parsers.py) |
| Produto | Texto usado para agrupar lote/resumo, derivado do PDF ou de mapeamentos | [parsers.py](../app/parsers.py), [cadastro.py](../app/cadastro.py) |
| MIOLO | Nome usado no mapa HP M, mapa Novakraft NEBX e grupo Cocelpa padrão | [parsers.py](../app/parsers.py) |
| KE | Marcador Cocelpa que altera todo o grupo para KRAFT ECOLOGICO | `_processar_coluna_cocelpa` em [parsers.py](../app/parsers.py) |
| Fabricação / lote / Cod. Bobinas | Campos do fornecedor usados como número da bobina nos parsers Cocelpa / Novakraft / HP | [parsers.py](../app/parsers.py) |
| Código de produto Novakraft | Letras + 3 dígitos de gramatura + 4 de diâmetro + 4 de formato; diferente do lote | `PADRAO_PRODUTO_NOVAKRAFT` em [parsers.py](../app/parsers.py) |
| Gramatura, formato, diâmetro | Campos nominais inteiros extraídos e enviados ao EGS; unidades não formalizadas no código | [modelos.py](../app/modelos.py) |
| Rua | Campo enviado ao EGS, padrão 1 na Bobina | [modelos.py](../app/modelos.py) |
| Peso | Inteiro em kg na Bobina; Cocelpa converte toneladas para kg | [parsers.py](../app/parsers.py) |
| Ajuste de peso | Soma separada de valores isolados reconhecidos no Cocelpa; participa do total geral/conferência final | `_tentar_valor_ajuste` e [cadastro.py](../app/cadastro.py) |
| Nota / registro | Seleção manual na tela EGS para classificar um produto; sem entidade local com ID | [cadastro.py](../app/cadastro.py) |
| Saldo a classificar | Peso restante lido da tela EGS e usado como limite preventivo | `ler_saldo_classificar` em [navegador.py](../app/navegador.py) |
| Quantidade classificada | Peso já classificado lido por método disponível; não usado pela orquestração atual | `ler_quantidade_classificada` em [navegador.py](../app/navegador.py) |
| Gramatura Média / Metragem | Campos calculados pelo EGS; automação só aguarda valores não vazios | `_esperar_calculo` em [navegador.py](../app/navegador.py) |
| Observação | Campo do EGS preenchido com número da bobina | `preencher_bobina` em [navegador.py](../app/navegador.py) |
| Histórico | Conjunto local de chaves de cadastros confirmados, persistido em JSON | [historico.py](../app/historico.py) |
| Ignoradas | Bobinas eliminadas pelo filtro inicial do histórico | [cadastro.py](../app/cadastro.py) |
| Pendentes / não processadas | Pendentes após filtro; na conclusão, não processadas = total − sucessos − falhas | [interface.py](../app/interface.py): `encerrar_cadastro` |
| Modal | Formulário/aviso sobre a lista; automação precisa aguardar e conferir seu estado | [navegador.py](../app/navegador.py) |
| Mock / simulador | HTML local que imita login, lista, formulário e saldo, sem backend EGS | [mock_sistema.html](../mock/mock_sistema.html) |
| Controle cooperativo | Pausa/interrupção atendida em pontos explícitos, sem cancelar operação em andamento | [controle.py](../app/controle.py) |
