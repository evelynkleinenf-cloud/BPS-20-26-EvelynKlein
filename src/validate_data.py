"""Valida o CSV salvo com DuckDB, independente da transformação pandas."""
import json
from decimal import Decimal
import duckdb
import pandas as pd
from .common import ROOT, EVIDENCE, YEARS, output_csv, sha256, write_json, now

def main():
    manifest = json.loads((EVIDENCE/'source_manifest.json').read_text(encoding='utf-8'))
    inventory = json.loads((EVIDENCE/'raw_inventory.json').read_text(encoding='utf-8'))
    con = duckdb.connect()
    con.read_csv(str(output_csv()), all_varchar=True).create_view('input_csv')
    con.sql('CREATE TABLE final_csv AS SELECT * FROM input_csv')
    checks = []
    def check(name, actual, expected):
        ok = actual == expected
        checks.append(dict(check=name, status='PASS' if ok else 'FAIL', actual=actual, expected=expected))
    expected_rows = sum(x['rows'] for x in inventory)
    check('linhas_antes_depois', con.sql('SELECT count(*) FROM final_csv').fetchone()[0], expected_rows)
    check('anos_exatos', [int(x[0]) for x in con.sql('SELECT DISTINCT ano_compra FROM final_csv ORDER BY ano_compra').fetchall()],list(YEARS))
    check('registro_id_unico',con.sql('SELECT count(DISTINCT registro_id) FROM final_csv').fetchone()[0],expected_rows)
    check('ano_compra_igual_ano_arquivo',con.sql('SELECT count(*) FROM final_csv WHERE ano_compra<>ano_arquivo').fetchone()[0],0)
    reconciliation=[]
    for source in manifest['files']:
        year=source['year']
        check(f'hash_origem_{year}',sha256(ROOT/source['csv_path']),source['csv_sha256'])
        con.read_csv(str(ROOT/source['csv_path']), delimiter=';', all_varchar=True).create_view('annual_raw', replace=True)
        raw=con.sql('''SELECT count(*), sum(CAST(vl_preco_total AS DECIMAL(30,4))),
            sum(CAST(qt_medicamento AS DECIMAL(30,4))) FROM annual_raw''').fetchone()
        final=con.execute('''SELECT count(*), sum(CAST(preco_total AS DECIMAL(30,4))),
            sum(CAST(quantidade AS DECIMAL(30,4))) FROM final_csv WHERE ano_compra=?''',[str(year)]).fetchone()
        for name,before,after in zip(['registros','preco_total','quantidade'],raw,final):
            check(f'{name}_{year}',after,before)
        reconciliation.append(dict(year=year,raw_rows=raw[0],final_rows=final[0],raw_value=str(raw[1]),final_value=str(final[1]),raw_quantity=str(raw[2]),final_quantity=str(final[2])))
    required=['ano_compra','registro_id','data_compra','preco_total','preco_unitario','quantidade','instituicao_id','fornecedor_id','codigo_catmat','uf']
    for col in required:
        check('obrigatorio_'+col,con.sql(f'SELECT count(*) FROM final_csv WHERE "{col}" IS NULL').fetchone()[0],0)
    check('ano_da_data',con.sql('SELECT count(*) FROM final_csv WHERE year(TRY_CAST(data_compra AS DATE))<>CAST(ano_compra AS INTEGER)').fetchone()[0],0)
    for col in ['data_compra','data_insercao']:
        check('tipo_data_'+col,con.sql(f'SELECT count(*) FROM final_csv WHERE "{col}" IS NOT NULL AND TRY_CAST("{col}" AS DATE) IS NULL').fetchone()[0],0)
    for col in ['preco_total','preco_unitario','quantidade']:
        check('numero_valido_'+col,con.sql(f'SELECT count(*) FROM final_csv WHERE "{col}" IS NOT NULL AND TRY_CAST("{col}" AS DECIMAL(30,4)) IS NULL').fetchone()[0],0)
        check('numero_positivo_'+col,con.sql(f'SELECT count(*) FROM final_csv WHERE CAST("{col}" AS DECIMAL(30,4))<=0').fetchone()[0],0)
    valid_uf='AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO'.split()
    ufs=[x[0] for x in con.sql('SELECT DISTINCT uf FROM final_csv').fetchall()]
    check('UFs_reconhecidas',sorted(set(ufs)-set(valid_uf)),[])
    check('quantidade_inteira',con.sql('SELECT count(*) FROM final_csv WHERE CAST(quantidade AS DECIMAL(30,4)) % 1<>0').fetchone()[0],0)
    columns=[x[0] for x in con.sql('DESCRIBE final_csv').fetchall()]
    nulls={c:con.sql(f'SELECT count(*) FROM final_csv WHERE "{c}" IS NULL').fetchone()[0] for c in columns}
    flags={c:con.sql(f'SELECT sum(CAST("{c}" AS BIGINT)) FROM final_csv').fetchone()[0] for c in columns if c.startswith('flag_')}
    totals=con.sql('''SELECT sum(CAST(preco_total AS DECIMAL(30,4))),sum(CAST(quantidade AS DECIMAL(30,4))),
        count(*),count(DISTINCT instituicao_id),count(DISTINCT fornecedor_id),count(DISTINCT fabricante_id) FROM final_csv''').fetchone()
    pmp=totals[0]/totals[1] if totals[1] else None
    # Independência: compara total informado com a multiplicação por registro sem reusar flags do ETL.
    delta=con.sql('''SELECT count(*) FROM final_csv WHERE abs(CAST(preco_total AS DECIMAL(30,4))-
        CAST(quantidade AS DECIMAL(18,0))*CAST(preco_unitario AS DECIMAL(18,4)))>0.01''').fetchone()[0]
    check('flag_total_reconciliada',flags['flag_total_divergente'],delta)
    results=dict(executed_at=now(),csv_sha256=sha256(output_csv()),status='PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL',
        checks=checks,reconciliation=reconciliation,nulls=nulls,flags=flags,
        kpis=dict(preco_total=str(totals[0]),quantidade=str(totals[1]),registros=totals[2],instituicoes=totals[3],fornecedores=totals[4],fabricantes=totals[5],preco_medio_ponderado=str(pmp)),
        notes=['PASS atesta a integridade técnica da transformação; inconsistências da fonte continuam sinalizadas.'])
    write_json(EVIDENCE/'validation.json',results)
    pd.DataFrame(reconciliation).to_csv(EVIDENCE/'reconciliation.csv',index=False)
    print(json.dumps(dict(status=results['status'],checks=len(checks),kpis=results['kpis'],flags=flags),ensure_ascii=True,indent=2),flush=True)
    if results['status']!='PASS':
        raise AssertionError('Validação falhou; consulte docs/evidence/validation.json')

if __name__=='__main__':
    main()

