# Histórico e estratégia de versionamento

O repositório foi criado em uma pasta própria para não misturar o projeto com o repositório pai. A sequência local inclui commits pequenos por funcionalidade:

- `chore: estrutura projeto e registra plano de execucao`
- `feat: adiciona download das bases BPS 2020-2026`
- `feat: padroniza colunas e tipos`
- `fix: corrige encoding dos arquivos anuais`
- `feat: consolida bases BPS 2020-2026`
- `feat: adiciona validacoes da base consolidada`
- `feat: cria KPIs obrigatorios`

Branches locais previstas: `main`, `develop`, `feature/download-bps`, `feature/data-cleaning`, `feature/data-consolidation`, `feature/kpis`, `feature/dashboard`, `feature/readme` e `feature/video`. O fluxo é feature → develop → main, com merges `--no-ff` para manter rastreabilidade.

O remoto deve ser criado como `evelynkleinenf-cloud/BPS-20-26-EvelynKlein`; após autenticar nessa conta, executar os comandos de publicação descritos no README.

