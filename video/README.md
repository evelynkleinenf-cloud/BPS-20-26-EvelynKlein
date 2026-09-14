# Apresentação — duração-alvo 4min45s

**Estado:** roteiro preparado; gravação com o rosto de Evelyn Klein e upload ainda dependem da aluna.
Não foi gerado um vídeo sintético nem uma gravação que substitua sua apresentação pessoal.

## Preparação

Abrir o dashboard em modo de leitura, a página de preços e o README. Colocar a webcam
no canto inferior sem cobrir filtros ou valores. Gravar em 1920×1080, iluminação frontal,
áudio testado e fonte legível. A resolução pode ser menor se continuar legível.
Gravar uma demonstração curta antes para conferir microfone e enquadramento.

## Roteiro cronometrado

| Tempo | Tela | Fala sugerida |
| --- | --- | --- |
| 0:00–0:25 | Rosto + cabeçalho | “Sou Evelyn Klein. Este projeto usa o Banco de Preços em Saúde para investigar a evolução e a concentração das compras registradas e identificar comparações de preço que merecem análise.” |
| 0:25–0:55 | README: fonte e plano | “Antes de desenvolver, organizei as tarefas em aquisição, diagnóstico, tratamento, validação, indicadores, dashboard e documentação. Usei exclusivamente os sete CSVs oficiais de 2020 a 2026, guardando URLs, datas e hashes dos arquivos.” |
| 0:55–1:30 | Relatório de qualidade | “Os sete anos tinham 36 colunas. Padronizei textos, datas, números e CNPJs. Corrigi 7.329 células com problemas recuperáveis de codificação. Concatenei 367.638 registros sem excluir linhas. As 54 verificações reconciliaram contagens, quantidades e valores; 12 datas de inserção e 170 possíveis repetições ficaram sinalizadas para investigação.” |
| 1:30–2:10 | Dashboard: KPIs e filtros | “Os seis indicadores são valor, quantidade, registros, instituições, fornecedores e preço médio ponderado. A ponderada é a soma do valor dividida pela soma da quantidade. Vou selecionar um ano e uma UF: os cartões e gráficos acompanham os filtros. Redefinir restaura a visão geral.” |
| 2:10–2:50 | Linha, UF, rankings | “O valor registrado totaliza R$ 115,12 bilhões. 2025 concentra R$ 50,90 bilhões, porém um único registro corresponde a 44,82% desse ano. Paraná e São Paulo lideram a concentração do snapshot. Pregão aparece em 90,45% dos registros. Esses números descrevem a base publicada e exigem leitura das limitações.” |
| 2:50–3:30 | Investigação de preço | “Para comparar preços, controlo produto, apresentação, fabricante, registro Anvisa, mês, UF, modalidade e faixa de quantidade. Em abril de 2021, um grupo de cinco compras comparáveis de sulfametoxazol com trimetoprima na Paraíba tem preços entre R$ 0,002 e R$ 0,27. Isso indica revisão de cadastro e contexto de negociação; não comprova sobrepreço ou irregularidade.” |
| 3:30–4:05 | Recomendações e limitações | “Recomendo revisar primeiro registros extremos que alteram os totais, monitorar grupos comparáveis e acompanhar concentração de fornecedores. Quantidades misturam unidades, os valores são nominais, há registros tardios e 2026 está parcial, com compras até 27 de agosto. Não atribuo causalidade às diferenças.” |
| 4:05–4:35 | Código e histórico Git | “O projeto tem módulos separados, testes, branches por funcionalidade e instruções de reprodução. Melhorias futuras incluem processamento em lotes, testes de integração no BI, comparação em janelas equivalentes e atualização automatizada com controle de versões das fontes.” |
| 4:35–4:45 | Rosto + links | “Os dados, métodos, resultados e limitações estão documentados no GitHub. O dashboard permite continuar a investigação com filtros.” |

Ensaiar e ajustar o ritmo; se ultrapassar 4min45s, reduzir pausas e detalhes sem omitir os dez temas.
Os números devem ser conferidos no dashboard antes da gravação e atualizados se houver novo snapshot.

## Arquivo e publicação

1. Gravar `apresentacao_EvelynKlein.mp4` com rosto e dashboard visíveis.
2. Verificar duração <300 segundos (alvo 285) e ouvir o vídeo inteiro.
3. Se couber no limite de arquivo do GitHub, colocar em `video/`; para arquivo maior,
   usar um release público do mesmo repositório e manter nesta pasta um README com o link.
4. Preferir MP4/H.264 com áudio AAC e bitrate ajustado à legibilidade.
5. Inserir o URL real em `project.json`, `README.md` e neste arquivo.
6. Conferir o link sem login. Não usar um URL fictício como evidência.

Checklist da gravação: [ ] duração [ ] rosto [ ] dashboard [ ] áudio [ ] objetivo
[ ] problema [ ] obtenção e consolidação [ ] tratamentos [ ] navegação [ ] KPIs
[ ] resultados [ ] recomendações [ ] organização prévia [ ] melhorias do código
[ ] upload público [ ] link no README.

A aluna deve substituir este roteiro pelo link real após a gravação; nenhum vídeo sintético é aceito como apresentação individual.

