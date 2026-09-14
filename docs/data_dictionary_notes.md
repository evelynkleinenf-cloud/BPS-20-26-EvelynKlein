# Notas do dicionário de dados

## Fonte oficial

O dicionário usado é o PDF publicado pelo Ministério da Saúde no recurso oficial do [Banco de Preços em Saúde (BPS)](https://dadosabertos.saude.gov.br/dataset/bps). A cópia usada para rastreabilidade está em [`docs/evidence/official_data_dictionary.pdf`](evidence/official_data_dictionary.pdf).

## Inventário dos arquivos

Os sete CSVs (2020 a 2026) têm o mesmo layout: 36 colunas, separador `;`, uma linha de cabeçalho e codificação UTF-8 nos arquivos disponibilizados. Não foram identificadas colunas ausentes, extras ou mudança na ordem durante o inventário. A diferença observada é de conteúdo: campos opcionais ficam vazios em proporções diferentes por ano e novas categorias de modalidade/unidade aparecem em alguns anos.

## Mapeamento para a base padronizada

| Campo do BPS | Campo consolidado | Uso |
|---|---|---|
| `ano_compra` | `ano_compra` | Ano e filtro temporal |
| `cnpj_instituicao`, `no_instituicao` | `cnpj_instituicao`, `instituicao` | Dimensão compradora |
| `sg_uf`, `no_municipio` | `uf`, `municipio` | Dimensões geográficas |
| `dt_compra` | `data_compra` | Linha do tempo |
| `co_catmat`, `ds_item` | `codigo_catmat`, `descricao_produto` | Produto |
| `cnpj_fornecedor`, `no_fornecedor` | `cnpj_fornecedor`, `fornecedor` | Fornecedor |
| `cnpj_fabricante`, `no_fabricante` | `cnpj_fabricante`, `fabricante` | Fabricante |
| `qt_medicamento` | `quantidade` | KPI de itens e ponderação |
| `vl_preco_unitario` | `preco_unitario` | Investigação comparável de preços |
| `vl_preco_total` | `preco_total` | KPI financeiro |
| `modalidade` | `modalidade_compra` | Composição por modalidade |
| `un_fornecimento`, `sg_unidade_medida` | `unidade_apresentacao`, `unidade_medida` | Controle de comparabilidade |
| `co_seq_bps` | `id_bps` | Identificador do registro |

## Regras de tipo e representação

- Identificadores e CNPJs permanecem como texto, preservando zeros à esquerda.
- Datas são convertidas para `datetime64` com coerção controlada; datas inválidas geram flag, não exclusão silenciosa.
- Quantidade, capacidade e preços são convertidos com `Decimal`/tipos numéricos; separadores e espaços são tratados antes da conversão.
- Categorias textuais são normalizadas com Unicode NFC, trim, colapso de espaços e caixa alta nas dimensões analíticas.
- Vazios são representados como nulo (`NA`) e contabilizados no relatório de qualidade.

## Discrepâncias de conteúdo

A estrutura é estável, mas as frequências de nulos mudam. Por exemplo, `generico`, `registro_anvisa`, `unidade_medida` e `observacao` têm maior ausência em alguns anos; `modalidade` recebe categorias adicionais (como `Diálogo Competitivo` em 2026). Esses valores foram mantidos e documentados, pois representam o registro publicado.

Foi detectado texto corrompido (mojibake) nos arquivos 2020–2023. A correção foi aplicada somente quando uma recodificação reversível reduziu marcadores de erro; 7.329 células foram corrigidas, sem alterar chaves numéricas.

## Capacidade e comparabilidade

O diagnóstico [`capacity_diagnostic.json`](evidence/capacity_diagnostic.json) encontrou 133.774 linhas comparáveis e nenhuma evidência para dividir ou multiplicar `capacidade_informada` por 100. A decisão foi preservar o valor fornecido e usar a apresentação/unidade textual para comparações. Diferenças de preço continuam sendo oportunidades de investigação, não prova de sobrepreço.

