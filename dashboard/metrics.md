# Contrato de métricas

Grão: um registro de item comprado publicado pelo BPS. Não é uma licitação inteira,
nota fiscal ou pedido único. Há várias linhas por instituição, processo e data.

| KPI | Base integral | Fonte compacta do Looker |
| --- | --- | --- |
| Valor Total Registrado | `SUM(preco_total)` | `SUM(preco_total)` |
| Quantidade Total de Itens Comprados | `SUM(quantidade)` | `SUM(quantidade)` |
| Número de Registros de Compra | `COUNT(registro_id)` | `SUM(registros)` ou Record Count |
| Instituições Compradoras | `COUNT_DISTINCT(instituicao_id)` | `COUNT_DISTINCT(instituicao)` |
| Fornecedores | `COUNT_DISTINCT(fornecedor_id)` | `COUNT_DISTINCT(fornecedor)` |
| Preço Unitário Médio Ponderado | `SUM(preco_total)/SUM(quantidade)` | mesma fórmula |

Fórmula calculada no Looker Studio, com proteção do denominador:

```text
CASE
  WHEN SUM(quantidade) > 0 THEN SUM(preco_total) / SUM(quantidade)
  ELSE NULL
END
```

Na extração validada todos os valores e quantidades são positivos e não nulos.
O valor financeiro é o informado pelo BPS: sua multiplicação por registro foi
conferida com Decimal e tolerância de R$ 0,01; nenhuma divergência foi encontrada.
Os valores armazenados mantêm até quatro casas decimais; arredondar a apresentação
em reais para duas casas não altera o armazenamento ou os somatórios.

Instituições e fornecedores são contados por CNPJ, tratado como texto com zeros à esquerda.
Se um CNPJ vier ausente/inválido em uma atualização, há fallback explícito por nome
(e localidade para instituição). O snapshot atual não precisou desse fallback.
Os rótulos compactos contêm chaves únicas e preservam exatamente essas contagens.
Cinco CNPJs de instituição apresentam variações de nome; o rótulo de BI usa o nome modal.

**Notas obrigatórias de leitura:**

- Quantidades somam unidades declaradas. Comprimidos, ampolas e mililitros não são uma
  única medida física; o total agregado não representa doses nem pacientes atendidos.
- A ponderada global mistura produtos, apresentações e unidades. É um indicador do
  conjunto filtrado; não é preço de mercado nem índice de inflação de medicamentos.
- Não somar preços unitários. Em rankings por valor, usar exclusivamente `preco_total`.
- Em preços, selecionar um produto e uma apresentação. Controlar fabricante, genérico,
  registro Anvisa, mês, UF, modalidade e faixa de quantidade. Examinar instituições e
  fornecedores separadamente. As condições contratuais e logísticas continuam desconhecidas.
- Ausência de resultados após filtros deve mostrar ausência, nunca ser substituída
  artificialmente por um preço médio de zero.
- Todas as medidas e gráficos usam a mesma fonte e o mesmo escopo de filtros da página.

## Referência numérica sem filtros

Consulte `docs/evidence/validation.json` (valores exatos) e `docs/evidence/filter_test_cases.json`
(cenários esperados). Não somar as contagens distintas de estados ou anos para obter
uma contagem distinta nacional.

