"""Append dos sete anos com preservação integral, saídas atômicas e Decimal."""
import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from .common import ROOT, YEARS, EVIDENCE, PROCESSED, setup, output_csv, sha256, write_json, now
from .inspect_data import read_raw
from .clean_data import clean_frame, COLUMN_MAP

def main():
    setup()
    frames, changes, samples = [], [], []
    for year in YEARS:
        frame, rules, examples = clean_frame(read_raw(year), year)
        frames.append(frame)
        changes.extend(rules)
        samples.extend(examples)
        print(f'{year}: {len(frame):,} linhas preservadas', flush=True)
    df = pd.concat(frames, ignore_index=True)
    assert len(df) == sum(map(len, frames))
    df['flag_duplicado_id_bps'] = (df['id_bps'].notna() & df['id_bps'].duplicated(keep=False)).astype('int8')
    original_cols = list(COLUMN_MAP.values())
    df['flag_duplicado_exato'] = df.duplicated(subset=original_cols, keep=False).astype('int8')
    business_cols = [c for c in original_cols if c not in ['id_bps', 'observacao', 'data_insercao']]
    df['flag_possivel_duplicado_negocio'] = df.duplicated(subset=business_cols, keep=False).astype('int8')
    target = output_csv()
    partial = target.with_suffix('.part')
    df.to_csv(partial, index=False, encoding='utf-8', sep=',', date_format='%Y-%m-%d', lineterminator='\n')
    partial.replace(target)
    table = pa.Table.from_pandas(df, preserve_index=False)
    parquet = PROCESSED / 'bps_20_26.parquet'
    pq.write_table(table, parquet, compression='zstd')
    pd.DataFrame(changes).to_csv(EVIDENCE / 'transformation_counts.csv',index=False,encoding='utf-8')
    pd.DataFrame(samples).to_csv(EVIDENCE / 'transformation_examples.csv',index=False,encoding='utf-8')
    write_json(EVIDENCE / 'consolidation.json',dict(generated_at=now(), years=list(YEARS), rows=len(df),
        columns=len(df.columns), rows_by_year={int(k):int(v) for k,v in df.groupby('ano_compra').size().items()},
        removed_rows=0, output_file=target.name, csv_sha256=sha256(target), csv_bytes=target.stat().st_size,
        parquet_sha256=sha256(parquet), parquet_schema=str(table.schema), dtypes={c:str(t) for c,t in df.dtypes.items()}))
    print(f'Consolidado: {len(df):,} registros; {len(df.columns)} colunas; {target.stat().st_size:,} bytes',flush=True)

if __name__ == '__main__':
    main()

