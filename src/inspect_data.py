"""Inventário integral dos arquivos, sem inferência destrutiva de tipos."""
import csv
import json
import pandas as pd
from .common import RAW, EVIDENCE, YEARS, setup, write_json

def read_raw(year):
    return pd.read_csv(RAW / f'BPS_{year}.csv', sep=';', encoding='utf-8-sig',
                       dtype='string', keep_default_na=False, on_bad_lines='error')

def main():
    setup()
    inventory = []
    reference = None
    for year in YEARS:
        path = RAW / f'BPS_{year}.csv'
        raw_bytes = path.read_bytes()
        text = raw_bytes.decode('utf-8-sig', errors='strict')
        df = read_raw(year)
        # csv.reader é uma segunda contagem independente do parser pandas.
        with path.open(encoding='utf-8-sig', newline='') as handle:
            rows = list(csv.reader(handle, delimiter=';'))
        nonempty = [r for r in rows if r]
        assert len(nonempty) - 1 == len(df), f'Contagem divergente: {year}'
        assert all(len(r) == len(df.columns) for r in nonempty), f'Estrutura irregular: {year}'
        columns = list(df.columns)
        if reference is None:
            reference = columns
        entry = dict(year=year, rows=len(df), independent_csv_rows=len(nonempty)-1,
                     columns_count=len(columns), columns=columns, encoding='UTF-8', separator=';',
                     blank_physical_records=len(rows)-len(nonempty),
                     replacement_characters=text.count('\ufffd'),
                     crcrlf_count=raw_bytes.count(b'\r\r\n'),
                     added_columns=sorted(set(columns)-set(reference)),
                     missing_columns=sorted(set(reference)-set(columns)),
                     column_order_equal=columns == reference,
                     empty_by_column={c:int(df[c].str.strip().eq('').sum()) for c in columns},
                     exact_duplicates=int(df.duplicated().sum()),
                     duplicate_source_ids=int(df['co_seq_bps'].duplicated().sum()),
                     year_values=df['ano_compra'].value_counts().to_dict(),
                     dates={}, numbers={}, categories={})
        for col in ['dt_compra', 'dt_insercao']:
            parsed = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
            entry['dates'][col] = dict(invalid=int((parsed.isna() & df[col].ne('')).sum()),
                                      min=str(parsed.min().date()), max=str(parsed.max().date()))
        for col in ['qt_medicamento', 'vl_preco_unitario', 'vl_preco_total', 'vl_capacidade']:
            nonblank = df[col][df[col].str.strip().ne('')]
            values = pd.to_numeric(nonblank, errors='coerce')
            entry['numbers'][col] = dict(invalid=int(values.isna().sum()),
                commas=int(nonblank.str.contains(',', regex=False).sum()),
                min=float(values.min()), max=float(values.max()),
                negative=int(values.lt(0).sum()), zero=int(values.eq(0).sum()),
                fractional_digits_max=int(nonblank.str.extract(r'\.(\d+)', expand=False).str.len().fillna(0).max()))
        for col in ['sg_uf', 'ds_esfera', 'fg_generico', 'tp_compra', 'modalidade', 'un_fornecimento', 'sg_unidade_medida']:
            entry['categories'][col] = df[col].value_counts(dropna=False).to_dict()
        inventory.append(entry)
        print(f'{year}: {len(df):,} registros; {len(columns)} colunas; duplicados={entry["exact_duplicates"]}', flush=True)
    write_json(EVIDENCE / 'raw_inventory.json', inventory)

if __name__ == '__main__':
    main()

