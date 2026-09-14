# BPS 2020–2026 — Compras registradas em saúde

**Mini-projeto individual de Visualização de Dados e Business Intelligence**  
**Aluna:** Evelyn Klein  
**Fonte:** Ministério da Saúde · Banco de Preços em Saúde  
**Snapshot:** 14/09/2026 · **367.638 registros** · **sete arquivos anuais**

> Os totais descrevem os registros publicados no BPS neste snapshot. Valores extremos,
> inserções tardias e cobertura variável exigem leitura crítica. 2026 é parcial,
> com compras informadas até **27/08/2026**. O projeto não certifica execução orçamentária,
> pagamentos, preços de mercado ou irregularidades.

## 1. Título do projeto

**BPS 2020–2026: evolução, concentração e investigação de preços das compras registradas em saúde.**

## 2. Objetivo

Consolidar os sete arquivos anuais, demonstrar a integridade do tratamento e permitir
investigações sobre período, localidade, comprador, produto, fornecedor e fabricante.
O dashboard combina visão gerencial com critérios de comparabilidade de preços.

## 3. Contextualização

Decisões de aquisição de medicamentos e insumos precisam considerar volume, apresentação,
fabricante, localidade e momento da compra. Uma média simples que mistura produtos pode
levar a interpretações inadequadas. BI organiza os registros e permite explorar essas
diferenças, desde que a qualidade e as limitações dos dados acompanhem os indicadores.

O BPS recebe informações de compras públicas e privadas. O recorte efetivamente baixado
contém as categorias de esfera descritas no inventário; não se presume que represente
todas as compras brasileiras nem toda a despesa do SUS. Não foram acrescentadas outras
bases, índices de inflação ou registros de outros anos.

## 4. Fonte dos dados

- Ministério da Saúde — [Banco de Preços em Saúde](https://dadosabertos.saude.gov.br/dataset/bps).
- [Recurso oficial do dicionário](https://dadosabertos.saude.gov.br/dataset/bps/resource/0e76f527-5e7e-417d-9d0b-f46d00afb717).
- [PDF de metadados, versão 07/04/2026](https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/BPS/Metadados_BPS_07_04_2026.pdf).
- Links, IDs, tamanho, data da obtenção e SHA-256 de cada arquivo:
  [manifesto de origem](docs/evidence/source_manifest.json).
- Cópia consultada do dicionário: [PDF](docs/evidence/official_data_dictionary.pdf).

As fontes continuam sujeitas a atualizações do publicador. A data do portal, a data do
dicionário, o ano da compra e a data de inserção são conceitos diferentes.

## 5. Período e cobertura

| Ano da compra | Registros | Colunas na origem | Maior data de compra |
| --- | ---: | ---: | --- |
| 2020 | 84.919 | 36 | 31/12/2020 |
| 2021 | 85.012 | 36 | 31/12/2021 |
| 2022 | 89.555 | 36 | 30/12/2022 |
| 2023 | 33.831 | 36 | 30/12/2023 |
| 2024 | 28.942 | 36 | 30/12/2024 |
| 2025 | 34.233 | 36 | 30/12/2025 |
| 2026 | 11.146 | 36 | 27/08/2026 |
| **Total** | **367.638** | **36 de origem; 70 na base final** | **2026 parcial** |

Preservação de todos os registros dos arquivos de 2020 a 2026. Nenhum outro ano foi
incluído. A base de 2026 não deve ser comparada diretamente com um ano completo para
afirmar crescimento ou queda anual.

## 6. Perguntas de negócio

1. Como evoluiu o valor registrado e a quantidade de registros por ano?
2. Quais UFs e municípios de localização dos compradores concentram maior valor?
3. Quais instituições, identificadas por CNPJ, têm maior participação?
4. Quais produtos e apresentações concentram valor e quantidade?
5. Quais fornecedores e fabricantes se destacam?
6. Quais modalidades predominam em número de registros e em valor?
7. Quanto os maiores registros influenciam os totais anuais?
8. Onde existem dispersões dentro de grupos com produto, apresentação, fabricante,
   Anvisa, mês, UF, modalidade e faixa de quantidade controlados?
9. Que problemas de preenchimento e possíveis repetições afetam a interpretação?

## 7. Processo de obtenção

`src/download_data.py` consulta o HTML público do portal e lê os metadados estruturados
incluídos na página. Seleciona exatamente um recurso **CSV** para cada ano solicitado.
O portal distribui esses CSVs em arquivos ZIP; o programa extrai apenas o CSV anual,
sem incorporar os recursos JSON, XML ou outros anos.

O download usa HTTPS, tentativas limitadas, verificação do tamanho informado pelo servidor,
leitura segura do ZIP e escrita temporária antes da substituição. O manifesto registra
SHA-256 do ZIP e do CSV, URL oficial, nome interno e cabeçalhos HTTP.
Em execução posterior, arquivos locais com hashes válidos são reutilizados. `--refresh`
baixa um novo snapshot e pode mudar os resultados. Não presumir que uma URL estável
continue servindo exatamente os mesmos bytes no futuro.

## 8. Preparação e transformação

**Python/pandas**, com valores monetários em `Decimal`, CSV UTF-8 e Parquet tipado.

1. Ler todas as colunas como texto, preservando zeros dos CNPJs e códigos.
2. Inventariar estrutura, formatos, nulos, categorias, intervalos e duplicidades de cada ano.
3. Mapear as 36 colunas para nomes sem acentos em `snake_case`.
4. Normalizar Unicode NFC e espaços; corrigir apenas mojibake recuperável com `ftfy`.
5. Converter vazios em nulos; nenhuma imputação de preço, quantidade ou nome.
6. Converter datas `DD/MM/AAAA` para datas e exportar `AAAA-MM-DD`.
7. Interpretar números com ponto decimal, sem separador de milhar na fonte observada.
   O parser também possui regra explícita e testada para formato brasileiro.
8. Padronizar categorias em maiúsculas, sem inferir equivalência entre nomes diferentes.
9. Preservar preço total informado e adicionar total calculado e flags de qualidade.
10. Fazer **append com `pandas.concat`**, na ordem 2020–2026, sem merge de consolidação.
11. Adicionar arquivo/ordinal de origem, identificador estável da linha e ano do arquivo.
12. Investigar duplicidades; **zero registros removidos**.

Evidências: [contagens por regra, ano e coluna](docs/evidence/transformation_counts.csv),
[exemplos antes/depois](docs/evidence/transformation_examples.csv) e
[relatório de qualidade](docs/data_quality_report.md).
Contagens de células alteradas não são somadas como se fossem pessoas ou compras distintas.

## 9. Discrepâncias entre anos

As sete extrações possuem os mesmos nomes, ordem e número de colunas. Não houve coluna
adicionada ou ausente entre esses arquivos. As diferenças observadas são de conteúdo:

- 7.329 células com mojibake recuperável: 1.876 em 2020, 1.955 em 2021,
  2.742 em 2022 e 756 em 2023; nenhuma em 2024–2026.
- Preenchimento de campos como genérico, Anvisa, observação e ata varia entre os anos.
- A cobertura cai de 89.555 registros/421 instituições em 2022 para
  33.831 registros/280 instituições em 2023; isso limita comparações do volume publicado.
- O PDF usa nomes descritivos e repete “Unidade de Fornecimento” para conceitos diferentes;
  o CSV distingue unidade, apresentação e capacidade. O mapeamento foi documentado.
- O campo numérico de capacidade apresenta diferenças de escala frente à apresentação
  textual. Foi preservado; a comparação utiliza a apresentação textual completa.
- Existem inserções tardias e 12 inserções datadas antes da compra. Permaneceram sinalizadas.
- O cabeçalho e as linhas usam `CR CR LF`, gerando linhas físicas vazias; a contagem é
  de registros CSV, não de quebras de linha. Nenhum registro de negócio foi descartado.

Detalhes e decisões: [notas do dicionário](docs/data_dictionary_notes.md) e
[inventário integral por ano](docs/evidence/raw_inventory.json).

## 10. Base consolidada

**`data/processed/BPS_20_26_EvelynKlein.csv`**  
367.638 registros · 70 colunas · UTF-8 · delimitador vírgula · ponto decimal · 315.526.356 bytes.

A base completa é gerada localmente pelo pipeline. Arquivos brutos e CSVs grandes são
ignorados pelo Git; não há amostragem substituindo a base final. O Parquet tipado
`data/processed/bps_20_26.parquet` é uma saída auxiliar, com valores decimais preservados.
O [manifesto da consolidação](docs/evidence/consolidation.json) registra hashes e tipos.

Para o Looker, `BPS_Looker_EvelynKlein.csv` mantém as mesmas linhas, medidas e dimensões
necessárias, usando rótulos compactos para caber no limite do conector. Os dicionários
completos ficam em `docs/evidence/bi_dictionaries/`. A correspondência é validada por ID.

## 11. Principais colunas

| Coluna | Significado |
| --- | --- |
| `ano_compra`, `data_compra` | Ano e data informados pela instituição |
| `data_insercao` | Data de inclusão no BPS; pode ser posterior ao ano da compra |
| `uf`, `municipio_uf` | Localização da instituição compradora, não necessariamente destino final |
| `instituicao_id`, `instituicao` | Identificador por CNPJ e nome do comprador |
| `fornecedor_id`, `fornecedor` | Identificador por CNPJ e nome do fornecedor |
| `fabricante_id`, `fabricante` | Identificador por CNPJ e nome do fabricante |
| `codigo_catmat`, `descricao_produto` | Identificação e descrição completa do item |
| `unidade_apresentacao` | Apresentação/unidade composta da fonte, essencial para comparação |
| `modalidade_compra`, `tipo_compra` | Modalidade declarada e natureza administrativa/judicial observada |
| `quantidade`, `preco_unitario`, `preco_total` | Quantidade, preço por unidade e valor total informado |
| `registro_anvisa`, `generico` | Características adicionais de comparabilidade, quando preenchidas |
| `id_bps`, `registro_id` | ID publicado e identificador único do registro no snapshot |
| `arquivo_origem`, `linha_origem`, `ano_arquivo` | Rastreabilidade até o arquivo e ordinal CSV original |
| `flag_*`, `elegivel_preco` | Sinalização técnica; não representa conclusão sobre regularidade |

## 12. KPIs e validação

| Indicador | Fórmula | Resultado integral |
| --- | --- | ---: |
| Valor Total Registrado | `SUM(preco_total)` | R$ 115.121.479.090,7891 |
| Quantidade Total de Itens Comprados | `SUM(quantidade)` | 64.811.007.566 |
| Número de Registros de Compra | `COUNT(registro_id)` | 367.638 |
| Instituições Compradoras | `COUNT_DISTINCT(instituicao_id)` | 854 |
| Fornecedores | `COUNT_DISTINCT(fornecedor_id)` | 3.671 |
| Preço Unitário Médio Ponderado | `SUM(preco_total)/SUM(quantidade)` | R$ 1,7762643016 |

No Looker, `SUM(registros)` conta as linhas e os rótulos únicos preservam as contagens
por CNPJ. Os indicadores devem sempre responder ao conjunto filtrado.
[Contrato completo de métricas](dashboard/metrics.md).

As **54 verificações independentes** em DuckDB passaram. Os valores, quantidades e
linhas de cada arquivo foram reconciliados com o CSV salvo. Os testes de tratamento
cobrem nulos versus zero, formatos numéricos, datas impossíveis, CNPJ e preservação
de registros. Os cenários de filtros de dados são separados dos testes da interface.

## 13. Metodologia da média ponderada

Preço ponderado = **soma do valor total / soma da quantidade**, calculado após os filtros.
Por exemplo, 10 unidades a R$ 2 e 90 unidades a R$ 4 resultam em R$ 3,80 por unidade;
a média simples de R$ 3,00 não representa o peso das quantidades.

O valor global mistura produtos e unidades; não deve ser utilizado como preço de
referência ou índice de inflação. Mesmo a quantidade total agrega unidades de fornecimento
heterogêneas e não equivale a doses, volume físico homogêneo ou pacientes.

A investigação de preços controla CATMAT, descrição, apresentação, fabricante, genérico,
Anvisa, mês, UF, modalidade e faixa de quantidade. Instituições, fornecedores e quantidades
exatas ainda variam dentro dos grupos: revisar os registros antes de qualquer conclusão.
**Nunca se soma preço unitário para construir um indicador financeiro.**

## 14. Dashboard e navegação

**[Abrir o relatório no Looker Studio](https://datastudio.google.com/reporting/98b84360-ce27-4ce7-a857-80bfe1c8a016)**

Começar pelo panorama, usar filtros de ano e UF e refinar por município, comprador,
fornecedor, fabricante, produto ou modalidade. Na investigação de preços, selecionar
produto e apresentação e controlar as características adicionais. Redefinir restaura
a visão inicial. A captura e os testes efetivamente realizados são registrados na auditoria.

- [Documentação de construção e navegação](dashboard/documentation.md).
- [Pasta de capturas do dashboard](dashboard/screenshots/).
- [Cenários esperados de filtros](docs/evidence/filter_test_cases.json).
- [Estado real da entrega e pendências](docs/final_audit.md).

## 15. Principais descobertas

- **2025 concentra R$ 50,90 bilhões**, mas o maior registro representa 44,82% do ano.
  A alta nominal de 460,06% ante 2024 exige revisão desses extremos e da cobertura.
- **PR e SP** concentram aproximadamente 74,44% do valor publicado. São Paulo/SP e
  Curitiba/PR lideram entre municípios de localização dos compradores.
- As secretarias estaduais de saúde identificadas pelos CNPJs `46374500026231` (SP)
  e `76416866000140` (PR) lideram o valor registrado por instituição.
- Penicilamina 250 mg/cápsula lidera por valor; a classificação é fortemente influenciada
  pelo registro BPS `15502366`, de R$ 22,816 bilhões, que deve ser conferido na origem.
- Dieta enteral CATMAT `404992`, em mililitros, lidera a quantidade registrada.
  A unidade impede interpretar esse ranking como comparação direta com comprimidos.
- AGILLE e PORTAL aparecem entre os fornecedores de maior valor; MEDQUIMICA e SUN
  entre fabricantes. A concentração é afetada pelos mesmos registros extremos.
- **Pregão** corresponde a 332.545 registros, aproximadamente 90,45% do total.
- A triagem encontrou **41 grupos** de preço com pelo menos cinco registros e dois
  fornecedores, sob os controles documentados. Um exemplo na PB, abril/2021,
  CATMAT `308882`, apresenta preços de R$ 0,002 a R$ 0,27: hipótese de investigação,
  com cinco instituições e quatro fornecedores, sem comprovação de irregularidade.

Tabelas, percentuais precisos, interpretação e análises de sensibilidade:
[análise dos resultados](docs/dashboard_analysis.md).

## 16. Recomendações

1. Priorizar a revisão dos maiores registros, pois poucos valores alteram o panorama
   anual e os rankings. Conferir quantidade, unidade, decimal e documento da aquisição.
2. Monitorar dispersões nos 41 grupos comparáveis e revisar primeiro observações muito
   distantes da mediana, preservando os registros e documentando a investigação.
3. Acompanhar fornecedores por produto/apresentação, sem confundir valor agregado com
   participação em um mercado definido ou qualidade do fornecimento.
4. Avaliar cobertura e atraso de inserção antes de comparar anos e regiões.
5. Corrigir preenchimento de datas, apresentação, genérico e Anvisa junto à fonte.

Evidência é o valor observado no snapshot; erros de cadastro, diferenças contratuais
ou condições de negociação são hipóteses que exigem confirmação externa.

## 17. Limitações

- Registro administrativo não comprova pagamento, entrega, consumo ou execução orçamentária.
- Compras podem ter fabricantes, apresentações, volumes, condições logísticas e negociais diferentes.
- 2026 está parcial; nenhuma queda anual de 2026 é apresentada como conclusão válida.
- Valores nominais: não foram corrigidos por inflação, por exigência de utilizar somente os CSVs do recorte.
- Cobertura institucional e regional varia entre anos; ausência de registro não significa ausência de compra.
- Há campos ausentes, datas inconsistentes, possíveis repetições e diferenças de escala na capacidade.
- CNPJ identifica estabelecimentos; não agrega automaticamente grupos econômicos ou governos inteiros.
- O PDF conceitual não descreve perfeitamente os 36 campos técnicos da versão atual.
- Os dados não identificam todas as condições contratuais; a análise é descritiva e não causal.
- CSV não preserva tipos por si só: configurar tipos de códigos, datas e medidas no BI.
- Rótulos do Looker são compactos; consultar os dicionários para nomes e descrições integrais.

## 18. Reprodução

Requisitos: Python 3.14, conexão à internet, Git e aproximadamente 2 GB livres para dados,
ambiente virtual e saídas. O processamento pode usar alguns GB de memória.

```powershell
git clone https://github.com/evelynkleinenf-cloud/BPS-20-26-EvelynKlein.git
cd BPS-20-26-EvelynKlein
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m src.run_pipeline
.\.venv\Scripts\python.exe -m pytest -q
```

Em Linux/macOS, usar `.venv/bin/python` no lugar de `.venv\Scripts\python.exe`.
O lock registra o ambiente utilizado; `requirements.txt` declara dependências diretas.

Etapas individuais: `src.download_data`, `src.inspect_data`, `src.consolidate_data`,
`src.validate_data`, `src.analyze_data`, `src.export_bi` e `src.verify_bi`, nessa ordem.
O pipeline interrompe em falhas. Para recalcular a base, as validações e os relatórios gerados: `python -m src.run_pipeline`.

Após a execução, conferir `docs/evidence/validation.json`, o CSV final e os hashes.
Seguir [a configuração do Looker](dashboard/documentation.md), aplicar os KPIs e testar os
filtros com os valores esperados. A reprodução da coleta atual pode diferir do snapshot
de 14/09/2026 se o Ministério substituir os arquivos; os hashes tornam essa mudança visível.

## 19. Estrutura e versionamento

```text
BPS-20-26-EvelynKlein/
├── README.md
├── project.json
├── requirements.txt
├── requirements-lock.txt
├── .gitignore
├── .github/workflows/quality.yml
├── data/
│   ├── raw/BPS_2020.csv ... BPS_2026.csv       # gerados, não versionados
│   ├── cache/2020.zip ... 2026.zip            # downloads originais
│   └── processed/
│       ├── BPS_20_26_EvelynKlein.csv
│       ├── bps_20_26.parquet
│       └── BPS_Looker_EvelynKlein.csv
├── src/                                    # download, ETL, validação, análise
├── tests/test_cleaning.py
├── docs/
│   ├── project_plan.md
│   ├── data_dictionary_notes.md
│   ├── data_quality_report.md
│   ├── dashboard_analysis.md
│   ├── final_audit.md
│   └── evidence/                           # inventários, hashes, testes, agregados
├── dashboard/
│   ├── metrics.md
│   ├── documentation.md
│   └── screenshots/
└── video/README.md
```

Branches por funcionalidade integram `develop` por merges explícitos; `main` recebe a
versão de entrega. Ver [plano inicial](docs/project_plan.md) e [histórico](docs/git_history.md).
Os commits registram incrementos reais, sem datas fabricadas ou histórico reescrito.

Código e textos preparados com assistência do Codex para este projeto; a aluna deve
revisar os resultados e apresentar sua compreensão. Os dados vêm exclusivamente das
fontes oficiais, sem copiar soluções de colegas.

## 20. Vídeo

**Gravação pendente da aluna.** [Roteiro completo de 4min45s e instruções de publicação](video/README.md).
O roteiro cobre objetivo, problema, dados, tratamento, filtros, KPIs, resultados,
recomendações, organização prévia e melhorias no código.

O link final será inserido após gravar com **rosto + dashboard**, verificar duração
menor que 5 minutos e publicar com acesso por link. Roteiro não equivale a vídeo entregue.

---

**Auditoria final:** [status critério por critério, evidências e correções restantes](docs/final_audit.md).
A menção a 13 critérios no enunciado não veio acompanhada da rubrica original com pesos;
a auditoria organiza os requisitos informados em 13 dimensões, sem prometer nota.

> Publicação: o relatório está configurado para acesso não listado como leitor; confirme o acesso sem login antes da entrega.

