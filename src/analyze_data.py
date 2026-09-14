"""Agregados e evidências analíticas reproduzíveis a partir de todas as linhas."""
import json
from decimal import Decimal
import duckdb
import pandas as pd
from .common import EVIDENCE, PROCESSED, write_json, now

def main():
    con=duckdb.connect()
    con.read_parquet(str(PROCESSED/'bps_20_26.parquet')).create_view('bps')
    tables={}
    dimensions={
        'anual':['ano_compra'], 'uf':['uf'], 'municipio':['municipio_uf'],
        'instituicao':['instituicao_id','instituicao'],
        'produto':['codigo_catmat','descricao_produto','unidade_apresentacao'],
        'fornecedor':['fornecedor_id','fornecedor'], 'fabricante':['fabricante_id','fabricante'],
        'modalidade':['modalidade_compra'], 'esfera':['esfera']}
    output=EVIDENCE/'analysis'
    output.mkdir(exist_ok=True)
    for name,dims in dimensions.items():
        if name in ['instituicao','fornecedor','fabricante']:
            by=name+'_id'
            select_dimensions=f'{by},min({name}) AS {name}'
        else:
            by=','.join(dims)
            select_dimensions=by
        query=f'''SELECT {select_dimensions},count(*) AS registros,sum(preco_total) AS valor_total,
            sum(quantidade) AS quantidade_total,count(DISTINCT instituicao_id) AS instituicoes,
            count(DISTINCT fornecedor_id) AS fornecedores,sum(preco_total)/sum(quantidade) AS preco_ponderado
            FROM bps GROUP BY {by} ORDER BY valor_total DESC'''
        df=con.sql(query).df()
        df.to_csv(output/f'{name}.csv',index=False,encoding='utf-8')
        tables[name]=df.head(10).to_dict(orient='records')
    con.sql('''SELECT * FROM bps ORDER BY preco_total DESC LIMIT 30''').df().to_csv(output/'maiores_registros.csv',index=False)
    by='codigo_catmat,descricao_produto,unidade_apresentacao,fabricante_id,generico,registro_anvisa,mes_compra,uf,modalidade_compra,faixa_quantidade'
    candidates=con.sql(f'''SELECT {by}, count(*) AS registros,count(DISTINCT instituicao_id) AS instituicoes,
        count(DISTINCT fornecedor_id) AS fornecedores,min(preco_unitario) AS minimo,
        quantile_cont(preco_unitario,0.25) AS p25,median(preco_unitario) AS mediana,
        quantile_cont(preco_unitario,0.75) AS p75,max(preco_unitario) AS maximo,
        max(preco_unitario)/min(preco_unitario) AS razao_max_min,
        sum(preco_total)/sum(quantidade) AS ponderado,min(quantidade) AS menor_quantidade,
        max(quantidade) AS maior_quantidade,sum(preco_total) AS valor_total
        FROM bps WHERE elegivel_preco=1 AND generico IS NOT NULL AND registro_anvisa IS NOT NULL
        GROUP BY {by} HAVING count(*)>=5 AND count(DISTINCT fornecedor_id)>=2
        ORDER BY razao_max_min DESC, registros DESC''').df()
    candidates.to_csv(output/'comparacoes_preco.csv',index=False,encoding='utf-8')
    topq=con.sql('''SELECT codigo_catmat,descricao_produto,unidade_apresentacao,sum(quantidade) AS quantidade,
        sum(preco_total) AS valor FROM bps GROUP BY ALL ORDER BY quantidade DESC LIMIT 20''').df()
    topq.to_csv(output/'produtos_quantidade.csv',index=False)
    annual=con.sql('''SELECT ano_compra,count(*) AS registros,sum(preco_total) AS valor_total,
        sum(quantidade) AS quantidade,count(DISTINCT instituicao_id) AS instituicoes,
        min(data_compra)::DATE AS primeira_compra,max(data_compra)::DATE AS ultima_compra,
        max(data_insercao)::DATE AS ultima_insercao,
        max(preco_total) AS maior_registro, max(preco_total)/sum(preco_total)*100 AS maior_registro_percentual
        FROM bps GROUP BY ano_compra ORDER BY ano_compra''').df()
    annual['variacao_nominal_percentual']=annual['valor_total'].pct_change()*100
    annual.to_csv(output/'evolucao_anual.csv',index=False)
    lag=con.sql('''SELECT ano_compra,count(*) FILTER(WHERE year(data_insercao)>ano_compra) AS inseridos_apos_ano,
        median(date_diff('day',data_compra,data_insercao)) AS mediana_dias,
        max(date_diff('day',data_compra,data_insercao)) AS maximo_dias FROM bps GROUP BY 1 ORDER BY 1''').df()
    lag.to_csv(output/'defasagem_insercao.csv',index=False)
    names={}
    for role in ['instituicao','fornecedor','fabricante']:
        df=con.sql(f'''SELECT {role}_id,count(DISTINCT {role}) AS nomes FROM bps
            GROUP BY 1 HAVING count(DISTINCT {role})>1 ORDER BY nomes DESC''').df()
        df.to_csv(output/f'variantes_nome_{role}.csv',index=False)
        names[role]=len(df)
    summary=dict(generated_at=now(),rankings=tables,annual=annual.to_dict('records'),
                 top_quantity=topq.head(10).to_dict('records'),price_comparisons=candidates.head(10).to_dict('records'),
                 comparison_groups=len(candidates),name_variants=names,
                 source_scope='Registros publicados pelo BPS; não representam automaticamente toda a despesa pública em saúde.')
    write_json(output/'summary.json',summary)
    print(json.dumps(summary,ensure_ascii=True,default=str)[:18000],flush=True)

if __name__=='__main__':
    main()

