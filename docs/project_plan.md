# Plano de execução individual

Planejado antes do tratamento e da construção do dashboard.

| Fase | Entrega | Dependência | Critério de aceite |
| --- | --- | --- | --- |
| A | Ambiente isolado e identificação do aluno | Nenhuma | Não alterar projetos existentes |
| B | Sete CSVs oficiais e manifesto SHA-256 | Portal oficial | Exatamente 2020–2026 |
| C | Inventário e diagnóstico | B | Estrutura e nulos de todos os anos |
| D | Padronização e append | C | Nenhuma remoção silenciosa |
| E | Reconciliação e qualidade | D | Linhas de origem = linhas finais |
| F | Seis KPIs e comparabilidade | E | Ponderada = soma total / soma quantidade |
| G | Dashboard com filtros e evidências | F | Testar oito filtros e pelo menos cinco visuais |
| H | README, análise e limitações | E–G | Vinte seções exigidas |
| I–J | GitHub e versionamento | Incremental | Branches reais e commits por entrega |
| K | Roteiro e gravação até 5 minutos | G–H | Aluno aparece junto ao dashboard |
| L | Auditoria da rubrica | Todas | Evidências e pendências explícitas |

O enunciado cita 13 critérios sem apresentar a rubrica original com seus nomes e pesos.
A auditoria agrupará os itens fornecidos em 13 dimensões operacionais, sem alegar
equivalência a uma pontuação oficial que não foi disponibilizada.

Decisões iniciais: Python/pandas para ETL; preservar todos os registros;
preferir Looker Studio e preparar Power BI se o acesso não permitir concluir no Looker;
nunca inventar dados, URLs de publicação, gravação, nome do aluno ou resultados.

