"""Reconcilia projeção BI e cenários de filtros com a base integral."""
import json
from decimal import Decimal
import duckdb
import pandas as pd
from .common import PROCESSED,EVIDENCE,write_json,sha256

def main():
    con=duckdb.connect()
    con.read_csv(str(PROCESSED/'BPS_Looker_EvelynKlein.csv'),all_varchar=True).create_view('bi_input')
    con.sql('CREATE TABLE bi AS SELECT * FROM bi_input')
    con.read_parquet(str(PROCESSED/'bps_20_26.parquet')).create_view('full_data')
    assert con.sql('SELECT count(*) FROM bi').fetchone()[0]==con.sql('SELECT count(*) FROM full_data').fetchone()[0]
    assert con.sql('SELECT count(*) FROM bi JOIN full_data USING(id_bps)').fetchone()[0]==con.sql('SELECT count(*) FROM bi').fetchone()[0]
    aliases={'ano_compra':'2022','uf':'PR','municipio':'CURITIBA / PR','modalidade':'PREGÃO'}
    for col in ['instituicao','fornecedor','fabricante','produto']:
        aliases[col]=con.sql(f'SELECT {col} FROM bi GROUP BY {col} ORDER BY count(*) DESC,{col} LIMIT 1').fetchone()[0]
    cases=[('sem_filtros',{})]+[(col,{col:value}) for col,value in aliases.items()]
    cases.append(('combinado',{'ano_compra':'2021','uf':'PB','modalidade':'PREGÃO'}))
    cases.append(('sem_resultados',{'uf':'INEXISTENTE'}))
    evidence=[]
    for name,filters in cases:
        where=' AND '.join(f'b."{k}"=?' for k in filters) or 'true'
        args=list(filters.values())
        fields='sum(CAST(b.preco_total AS DECIMAL(30,4))),sum(CAST(b.quantidade AS DECIMAL(30,4))),count(*),count(DISTINCT b.instituicao),count(DISTINCT b.fornecedor)'
        got=con.execute(f'SELECT {fields} FROM bi b WHERE {where}',args).fetchone()
        expected=con.execute(f'''SELECT sum(f.preco_total),sum(f.quantidade),count(*),count(DISTINCT f.instituicao_id),count(DISTINCT f.fornecedor_id)
            FROM full_data f JOIN bi b USING(id_bps) WHERE {where}''',args).fetchone()
        assert got==expected,(name,got,expected)
        evidence.append(dict(case=name,filters=filters,status='PASS_DATA',preco_total=str(got[0]) if got[0] is not None else None,
            quantidade=str(got[1]) if got[1] is not None else None,registros=got[2],instituicoes=got[3],fornecedores=got[4],
            preco_ponderado=str(got[0]/got[1]) if got[1] else None,
            manual_dashboard_status='PENDENTE'))
    write_json(EVIDENCE/'filter_test_cases.json',evidence)
    # Garante correspondência de todas as medidas por ID e não só do somatório.
    mismatches=con.sql('''SELECT count(*) FROM bi b JOIN full_data f USING(id_bps)
        WHERE CAST(b.preco_total AS DECIMAL(30,4))<>f.preco_total OR CAST(b.quantidade AS DECIMAL(30,4))<>f.quantidade
        OR CAST(b.preco_unitario AS DECIMAL(30,4))<>f.preco_unitario''').fetchone()[0]
    assert mismatches==0
    write_json(EVIDENCE/'bi_validation.json',dict(status='PASS',filter_cases=len(evidence),row_measure_mismatches=mismatches,
        sha256=sha256(PROCESSED/'BPS_Looker_EvelynKlein.csv'),actual_ui_verified=False))
    df=con.sql('SELECT * FROM full_data').df()
    # Valores de capacidade parecem escalados em relação à apresentação textual; preservar, não dividir automaticamente.
    textual=pd.to_numeric(df['unidade_apresentacao'].str.extract(r'(\d+[,.]\d+)',expand=False).str.replace(',','.',regex=False),errors='coerce')
    numeric=pd.to_numeric(df['capacidade_informada'],errors='coerce')
    comparable=textual.notna() & numeric.notna() & textual.gt(0)
    ratio=numeric[comparable]/textual[comparable]
    capacity=dict(comparable_rows=int(comparable.sum()),equal=int(ratio.eq(1).sum()),ratio_100=int(ratio.sub(100).abs().lt(1e-6).sum()),
                  action='Nenhuma correção de escala: usar apresentação textual na comparabilidade e manter capacidade_informada como fornecida.')
    write_json(EVIDENCE/'capacity_diagnostic.json',capacity)
    df.loc[df['flag_insercao_anterior_compra'].eq(1),['registro_id','id_bps','arquivo_origem','linha_origem','data_compra','data_insercao']].to_csv(EVIDENCE/'inconsistent_dates.csv',index=False)
    df.loc[df['flag_possivel_duplicado_negocio'].eq(1),['registro_id','id_bps','arquivo_origem','linha_origem','codigo_catmat','unidade_apresentacao','instituicao_id','data_compra','preco_total']].to_csv(EVIDENCE/'possible_duplicates.csv',index=False)
    print(f'{len(evidence)} cenários de dados reconciliados; nenhuma diferença nas medidas por registro. Testes de UI continuam separados.')

if __name__=='__main__':
    main()

