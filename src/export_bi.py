"""Projeção por registro para Looker; rótulos curtos com chaves sem colisão.

A base histórica integral continua preservada. Este CSV mantém TODAS as linhas,
medidas, filtros e apresentação; dicionários ligam os rótulos às descrições completas.
"""
import hashlib
import json
import pandas as pd
from .common import PROCESSED, EVIDENCE, write_json, sha256

def compact_labels(df, id_col, name_col, prefix, max_chars):
    distinct=df[[id_col,name_col]].dropna(subset=[id_col]).copy()
    distinct[name_col]=distinct[name_col].fillna('NOME NÃO INFORMADO')
    # Nome modal por identificador; empate resolvido lexicalmente, de modo determinístico.
    counts=distinct.value_counts().rename('ocorrencias').reset_index()
    canonical=counts.sort_values([id_col,'ocorrencias',name_col],ascending=[True,False,True]).drop_duplicates(id_col)
    canonical=canonical.sort_values(id_col).reset_index(drop=True)
    canonical['rotulo']=canonical[name_col].str.slice(0,max_chars)+' ['+prefix+canonical.index.to_series().add(1).astype(str).str.zfill(4)+']'
    assert canonical['rotulo'].is_unique
    return df[id_col].map(canonical.set_index(id_col)['rotulo']),canonical

def main():
    df=pd.read_parquet(PROCESSED/'bps_20_26.parquet')
    out=pd.DataFrame(index=df.index)
    out['ano_compra']=df['ano_compra']
    out['uf']=df['uf']
    out['municipio']=df['municipio_uf']
    dictionaries=EVIDENCE/'bi_dictionaries'
    dictionaries.mkdir(exist_ok=True)
    for entity,prefix in [('instituicao','I'),('fornecedor','F'),('fabricante','M')]:
        out[entity],dictionary=compact_labels(df,entity+'_id',entity,prefix,24)
        dictionary.to_csv(dictionaries/f'{entity}.csv',index=False,encoding='utf-8')
    # Descrição CATMAT completa define a identidade; rótulo curto só é apresentação.
    out['produto'],dictionary=compact_labels(df.assign(produto_nome=df['produto']),'produto','produto_nome','P',55)
    dictionary.to_csv(dictionaries/'produto.csv',index=False,encoding='utf-8')
    out['apresentacao']=df['unidade_apresentacao']
    out['modalidade']=df['modalidade_compra']
    out['data_compra']=df['data_compra'].dt.strftime('%Y%m%d')
    out['quantidade']=df['quantidade'].map(lambda x: format(x,'f') if x is not None else '')
    out['preco_total']=df['preco_total'].map(lambda x: format(x.normalize(),'f') if x is not None else '')
    out['preco_unitario']=df['preco_unitario'].map(lambda x: format(x.normalize(),'f') if x is not None else '')
    out['registros']=1
    out['generico']=df['generico']
    out['registro_anvisa']=df['registro_anvisa']
    out['faixa_quantidade']=df['faixa_quantidade'].str.slice(0,2)
    out['elegivel_preco']=df['elegivel_preco']
    out['id_bps']=df['id_bps']
    out['mes_compra']=df['mes_compra']
    out['total_divergente']=df['flag_total_divergente']
    target=PROCESSED/'BPS_Looker_EvelynKlein.csv'
    out.to_csv(target,index=False,encoding='utf-8',lineterminator='\n')
    assert len(out)==len(df)
    assert out['registros'].sum()==len(df)
    for entity in ['instituicao','fornecedor','fabricante']:
        assert out[entity].nunique()==df[entity+'_id'].nunique()
    assert target.stat().st_size<100_000_000, f'Projeção ultrapassou limite: {target.stat().st_size}'
    write_json(EVIDENCE/'bi_export.json',dict(path=str(target.name),rows=len(out),columns=list(out.columns),
        bytes=target.stat().st_size,sha256=sha256(target),row_aggregation=False,removed_rows=0,
        label_policy='Nome modal por ID, prefixo legível e chave sequencial única; dicionários completos em bi_dictionaries. Rótulos mudam se o universo de IDs mudar: substituir integralmente a fonte em atualizações.',
        warning='Não fazer append de uma nova extração completa na mesma fonte do Looker: duplicaria os registros.'))
    print(f'Looker: {len(out):,} registros; {target.stat().st_size:,} bytes',flush=True)

if __name__=='__main__':
    main()

