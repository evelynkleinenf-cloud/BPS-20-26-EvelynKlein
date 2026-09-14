# Dashboard BPS — Evelyn Klein

Relatório publicado para leitura: <https://datastudio.google.com/reporting/98b84360-ce27-4ce7-a857-80bfe1c8a016>.
O estado de publicação e os testes efetivamente executados constam em `docs/final_audit.md`.

## Fonte e importação

1. Executar o pipeline e conferir `validation.json`: status PASS.
2. Abrir o relatório com a conta de Evelyn Klein.
3. Conectar **Upload de arquivos CSV**, criando um conjunto `BPS_2020_2026_EvelynKlein`.
4. Enviar `data/processed/BPS_Looker_EvelynKlein.csv` uma única vez.
5. A fonte possui todas as 367.638 linhas da base integral, sem agregação ou exclusão.
   A projeção reduz colunas e abrevia rótulos para caber no limite de 100 MB por conjunto.
6. Configurar `ano_compra` como número sem agregação; `data_compra` como data `YYYYMMDD`;
   `id_bps` e `registro_anvisa` como texto. `preco_total`, `quantidade`, `registros` como soma;
   `preco_unitario` como média somente para inspeção de registros, nunca soma.
7. Criar o campo calculado de preço ponderado de `metrics.md` e os seis cartões.
   No relatório atual, o cartão exibe `SUM(preco_total) / SUM(quantidade)` e retorna
   R$ 1,78 no filtro completo.
8. Em novas extrações, criar uma fonte substituta ou substituir os arquivos da anterior.
   Não acrescentar novamente o snapshot completo: o conector faz append e duplicaria tudo.

Os rótulos `[Ixxxx]`, `[Fxxxx]`, `[Mxxxx]`, `[Pxxxx]` são chaves de apresentação.
Os dicionários em `docs/evidence/bi_dictionaries/` associam-nos aos CNPJs e descrições
completas. Um prefixo abreviado não é critério de comparabilidade: a chave preserva a
descrição inteira. Como chaves sequenciais dependem do universo do snapshot, regenerar
todos os arquivos e substituir integralmente a fonte em uma atualização.

## Layout previsto

Paleta: azul profundo `#123047`, verde saúde `#137C74`, verde claro `#E9F5F1`,
fundo `#F5F8FA`, texto `#223B4B`, âmbar `#B36B00` para limitações.
Fonte Arial/Roboto, títulos 20–28 px, corpo 12–14 px, cartões 24–32 px.

### Página 1 — Panorama das compras (implementada no relatório)

- Cabeçalho: BPS | Compras registradas em saúde — 2020–2026.
- Subtítulo: cobertura do snapshot oficial; 2026 até 27/08, período parcial.
- Seis KPIs de `metrics.md`.
- Filtros interativos configurados: ano, UF, modalidade, produto, fornecedor e fabricante.
  Município e instituição permanecem disponíveis como dimensões dos rankings e podem ser
  adicionados como controles em uma iteração posterior.
- Linha mensal: `mes_compra` crescente × soma do preço total (com série auxiliar de registros).
- Barras horizontais: UF e município × soma do preço total.
- Ranking de instituições: instituição × soma do preço total.
- Modalidades: barras por soma dos registros; tooltip ou tabela inclui valor.
- Produtos: produto + apresentação × valor e quantidade.
- Fornecedores e fabricantes: rankings por valor.

### Página 2 — Investigação de preços

- Controles de produto, apresentação, fabricante, genérico, registro Anvisa, mês,
  UF, modalidade, faixa de quantidade e instituição/fornecedor.
- Seis KPIs no mesmo contexto de filtros.
- Tabela dos registros: ID, data, instituição, fornecedor, quantidade,
  preço unitário, preço total, genérico e Anvisa.
- Comparação por fornecedor com preço ponderado, mínimo, máximo e registros.
- Nota permanente: dispersão sugere investigação; não demonstra irregularidade.

## Navegação e teste

Começar sem filtros, selecionar ano, refinar UF e município, depois produto/apresentação.
Usar a opção Redefinir para retornar ao total. Para preço, aplicar os controles adicionais.
Conferir se os seis cartões mudam juntos. Um filtro que não altere determinada métrica
não é necessariamente erro: comparar com o cenário independente esperado.

`docs/evidence/filter_test_cases.json` contém oito testes individuais, um teste combinado
e um filtro sem resultados, calculados sobre as linhas da projeção e reconciliados com a base.
Registrar o que foi realmente observado em `docs/evidence/dashboard_manual_tests.csv`.
Testes de dados não substituem a interação real com o dashboard publicado.

## Compartilhamento e evidências

- O acesso geral foi configurado como **Não listado / Leitor**; o link acima é a URL pública.
- A interface foi verificada no editor: seis cartões, linha mensal, três rankings em barras,
  pizza de modalidade, tabela de produtos e seis controles aparecem no canvas.
- Salvar capturas adicionais em `dashboard/screenshots/`, com filtros visíveis e data da captura,
  e executar os cenários de seleção em `dashboard_manual_tests.csv` antes da entrega final.
- Os testes de dados não substituem a interação real; a auditoria mantém essa pendência explícita.

Referência técnica: [conector CSV e limites oficiais](https://docs.cloud.google.com/data-studio/upload-csv-files).

Última verificação visual no editor: 14/09/2026, com fonte conectada e acesso não listado/leitor.

