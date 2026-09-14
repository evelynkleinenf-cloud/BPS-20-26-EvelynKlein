# Histórico e estratégia de versionamento

O repositório foi criado em uma pasta própria para não misturar o projeto com o repositório pai. A sequência local inclui commits pequenos por funcionalidade:

- `chore: estrutura projeto e registra plano de execucao`
- `feat: adiciona download das bases BPS 2020-2026`
- `feat: padroniza colunas e tipos`
- `fix: corrige encoding dos arquivos anuais`
- `feat: consolida bases BPS 2020-2026`
- `feat: adiciona validacoes da base consolidada`
- `feat: cria KPIs obrigatorios`

Branches locais e remotas: `main`, `develop`, `feature/download-bps`, `feature/data-cleaning`, `feature/data-consolidation`, `feature/kpis`, `feature/dashboard`, `feature/readme` e `feature/video`. O fluxo é feature → develop → main, com merges `--no-ff` para manter rastreabilidade.

O remoto público foi criado em `https://github.com/evelynkleinenf-cloud/BPS-20-26-EvelynKlein` e recebeu o commit de entrega `05ac0066529539057e353ec3f8e8676d35de1e73`. A comprovação das refs publicadas está em `docs/evidence/remote_publication.json`. Os arquivos brutos e as saídas grandes continuam fora do Git e são reproduzidos pelo pipeline.

