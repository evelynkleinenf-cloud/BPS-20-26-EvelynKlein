# Relatório de qualidade dos dados

**Escopo:** BPS 2020–2026, obtido do portal oficial em 14/09/2026.

## Reconciliação de linhas

| Ano | Linhas no CSV | Linhas consolidadas |
|---:|---:|---:|
| 2020 | 84.919 | 84.919 |
| 2021 | 85.012 | 85.012 |
| 2022 | 89.555 | 89.555 |
| 2023 | 33.831 | 33.831 |
| 2024 | 28.942 | 28.942 |
| 2025 | 34.233 | 34.233 |
| 2026 | 11.146 | 11.146 |
| **Total** | **367.638** | **367.638** |

Não houve remoção de linhas (`removed_rows = 0`). A consolidação tem 70 colunas, incluindo campos padronizados, chaves técnicas e flags de qualidade. A evidência detalhada está em [`consolidation.json`](evidence/consolidation.json) e [`reconciliation.csv`](evidence/reconciliation.csv).

## Validações executadas

O script `python -m src.validate_data` executou 54 verificações e retornou **PASS** em [`validation.json`](evidence/validation.json): anos exatos, soma antes/depois, identificador BPS único, tipos, datas, números, sinais, CNPJs, divergência entre total e quantidade × preço e categorias.

| Indicador | Resultado |
|---|---:|
| Registros finais | 367.638 |
| IDs BPS duplicados | 0 |
| Duplicidades exatas | 0 |
| Quantidades não positivas | 0 |
| Preços unitários negativos | 0 |
| Preços totais negativos | 0 |
| Datas de compra inválidas | 0 |
| Números inválidos | 0 |
| Divergência material `preco_total` vs. cálculo | 0 |
| Possíveis duplicidades de negócio | 170 |
| Inserção anterior à compra | 12 |

As 170 possíveis duplicidades de negócio e as 12 inserções anteriores são flags para investigação; não foram excluídas porque podem representar compras legítimas ou atualização tardia do cadastro.

## Nulos e vazios

Os nulos são preservados e reportados por coluna. No consolidado, exemplos são: `data_insercao` 2.142; `generico` e `registro_anvisa` 179.729 cada; `unidade_medida` 233.829; `observacao` 58.772. Campos obrigatórios para os KPIs (`ano_compra`, `data_compra`, `quantidade`, `preco_total`, `id_bps`) não apresentam nulos inválidos.

## Transformações rastreáveis

As contagens por regra estão em [`transformation_counts.csv`](evidence/transformation_counts.csv) e exemplos em [`transformation_examples.csv`](evidence/transformation_examples.csv). Foram aplicados: trim/Unicode NFC; correção de mojibake reversível; vazio→NA; normalização de categorias; parsing de datas; parsing numérico; criação de chaves e flags. Os arquivos de origem não são alterados.

## Medidas financeiras

Todos os preços são não negativos. O total consolidado é R$ 115.121.479.090,79. O preço unitário médio ponderado é calculado como `SUM(preco_total) / SUM(quantidade)` = R$ 1,7763 por unidade no filtro completo.

## Reprodução

Execute `python -m src.run_pipeline` após instalar `requirements.txt`. O pipeline falha de forma explícita em inconsistências críticas, grava evidências em `docs/evidence/` e mantém o histórico anual completo.

