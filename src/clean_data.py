"""Padronização conservadora; todas as linhas são preservadas e auditadas."""
from decimal import Decimal, InvalidOperation
import re
import unicodedata
import pandas as pd
from ftfy import fix_encoding

COLUMN_MAP = {
    'ano_compra':'ano_compra', 'cnpj_instituicao':'cnpj_instituicao', 'sg_uf':'uf',
    'ds_esfera':'esfera', 'dt_compra':'data_compra', 'dt_insercao':'data_insercao',
    'validade_compra':'validade_compra', 'co_catmat':'codigo_catmat', 'ds_item':'descricao_produto',
    'co_pdm':'codigo_pdm', 'co_grupo':'codigo_grupo', 'no_grupo':'grupo',
    'co_classe':'codigo_classe', 'no_classe':'classe', 'fg_generico':'generico',
    'tp_compra':'tipo_compra', 'sg_unidade_medida':'unidade_medida',
    'cnpj_fornecedor':'cnpj_fornecedor', 'no_fornecedor':'fornecedor',
    'cnpj_fabricante':'cnpj_fabricante', 'no_fabricante':'fabricante',
    'qt_medicamento':'quantidade', 'ds_observacao':'observacao',
    'no_instituicao':'instituicao', 'no_municipio':'municipio',
    'un_medida_capacidade':'unidade_apresentacao', 'no_pdm':'pdm',
    'nu_processo_compra':'numero_processo', 'nu_ata':'numero_ata',
    'un_fornecimento':'unidade_fornecimento', 'registro_anvisa':'registro_anvisa',
    'modalidade':'modalidade_compra', 'vl_capacidade':'capacidade_informada',
    'vl_preco_unitario':'preco_unitario', 'vl_preco_total':'preco_total', 'co_seq_bps':'id_bps'
}
NUMBERS = ['quantidade', 'preco_unitario', 'preco_total', 'capacidade_informada']
DATES = ['data_compra', 'data_insercao']
CATEGORIES = ['uf', 'esfera', 'instituicao', 'municipio', 'fornecedor', 'fabricante',
              'descricao_produto', 'unidade_medida', 'unidade_apresentacao',
              'unidade_fornecimento', 'modalidade_compra', 'tipo_compra', 'generico']

def normalize_text(value):
    # Somente reversão de mojibake reconhecido, NFC e espaços; sem adivinhar acentos.
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', fix_encoding(str(value)))).strip()

def decimal_value(value):
    """Aceita formatos documentados; valores ambíguos/ilegais permanecem ausentes."""
    value = str(value).strip()
    if not value:
        return None
    if ',' in value:
        if re.fullmatch(r'[+-]?(?:\d{1,3}(?:\.\d{3})+|\d+),\d+', value):
            value = value.replace('.', '').replace(',', '.')
        else:
            return None
    if not re.fullmatch(r'[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?', value):
        return None
    try:
        parsed = Decimal(value)
        return parsed if parsed.is_finite() else None
    except InvalidOperation:
        return None

def identity(cnpj, names, geo=None):
    valid = cnpj.str.fullmatch(r'\d{14}', na=False) & ~cnpj.isin([str(digit)*14 for digit in range(10)])
    fallback = 'NOME:' + names
    if geo is not None:
        fallback = fallback + '|' + geo
    result = cnpj.where(valid, fallback)
    return result.mask(~valid & names.isna())

def clean_frame(raw, year):
    if set(raw.columns) != set(COLUMN_MAP):
        raise ValueError(f'Esquema mudou em {year}; atualizar mapeamento antes de processar.')
    df = raw.rename(columns=COLUMN_MAP).copy()
    changes = []
    audit_samples = []
    for col in df.columns:
        original = df[col].copy()
        unique = original.drop_duplicates()
        mapping = {x: normalize_text(x) for x in unique}
        df[col] = original.map(mapping).astype('string')
        changed = original.ne(df[col])
        encoding_changes = sum(int(original.eq(x).sum()) for x in unique if fix_encoding(str(x)) != str(x))
        if changed.any():
            for idx in df.index[changed][:10]:
                audit_samples.append(dict(year=year, source_row=int(idx)+1, column=col,
                                          before=original.at[idx], after=df.at[idx,col], rule='texto_NFC_espacos_encoding'))
        changes.append(dict(year=year, column=col, rule='texto_NFC_espacos_encoding',
                            affected=int(changed.sum()), encoding_fixed=encoding_changes))
        blank = df[col].eq('')
        changes.append(dict(year=year, column=col, rule='vazio_para_nulo', affected=int(blank.sum())))
        df[col] = df[col].mask(blank)
        if col in CATEGORIES:
            old = df[col].copy()
            df[col] = df[col].str.upper()
            changes.append(dict(year=year, column=col, rule='categoria_caixa_alta', affected=int((old.ne(df[col])).sum())))
    for col in NUMBERS:
        original = df[col].copy()
        mapping = {x: decimal_value(x) for x in original.dropna().unique()}
        parsed = original.map(mapping)
        df[col] = pd.Series(parsed, index=df.index, dtype=object).where(original.notna(), None)
        df['flag_invalido_' + col] = (original.notna() & df[col].isna()).astype('int8')
        changes.append(dict(year=year, column=col, rule='conversao_decimal_exata',
                            affected=int(original.notna().sum()), invalid=int(df['flag_invalido_'+col].sum())))
    for col in DATES:
        original = df[col].copy()
        df[col] = pd.to_datetime(original, format='%d/%m/%Y', errors='coerce')
        df['flag_invalido_' + col] = (original.notna() & df[col].isna()).astype('int8')
        changes.append(dict(year=year, column=col, rule='data_dd_mm_aaaa_para_ISO', affected=int(original.notna().sum()), invalid=int(df['flag_invalido_'+col].sum())))
    df['ano_compra'] = pd.to_numeric(df['ano_compra'], errors='raise').astype('Int64')
    # Nunca substituir ano da compra pelo nome do arquivo silenciosamente.
    if not df['ano_compra'].eq(year).all():
        raise ValueError(f'Ano da compra diverge do arquivo {year}. Investigar sem excluir linhas.')
    for col in ['cnpj_instituicao', 'cnpj_fornecedor', 'cnpj_fabricante']:
        original = df[col].copy()
        df[col] = df[col].str.replace(r'[./\-\s]', '', regex=True)
        changes.append(dict(year=year, column=col, rule='retira_pontuacao_CNPJ_preserva_zeros', affected=int(original.ne(df[col]).sum())))
        df['flag_formato_' + col] = (df[col].notna() & ~df[col].str.fullmatch(r'\d{14}', na=False)).astype('int8')
    df['ano_arquivo'] = year
    df['arquivo_origem'] = f'BPS_{year}.csv'
    df['linha_origem'] = range(1, len(df)+1)  # ordinal do registro após o cabeçalho, não linha física
    df['registro_id'] = str(year) + ':' + df['linha_origem'].astype(str)
    df['instituicao_id'] = identity(df['cnpj_instituicao'], df['instituicao'], df['uf'].fillna('')+'|'+df['municipio'].fillna(''))
    df['fornecedor_id'] = identity(df['cnpj_fornecedor'], df['fornecedor'])
    df['fabricante_id'] = identity(df['cnpj_fabricante'], df['fabricante'])
    df['municipio_uf'] = df['municipio'] + ' / ' + df['uf']
    df['produto'] = df['codigo_catmat'] + ' | ' + df['descricao_produto']
    df['mes_compra'] = df['data_compra'].dt.strftime('%Y-%m')
    df['trimestre_compra'] = df['data_compra'].dt.to_period('Q').astype('string')
    df['flag_ano_data_divergente'] = df['data_compra'].dt.year.ne(df['ano_compra']).fillna(True).astype('int8')
    df['flag_data_futura'] = df['data_compra'].gt(pd.Timestamp.now().normalize()).astype('int8')
    df['flag_insercao_anterior_compra'] = df['data_insercao'].lt(df['data_compra']).astype('int8')
    total_calculado, diferenca, divergencia = [], [], []
    for q, p, t in zip(df['quantidade'], df['preco_unitario'], df['preco_total']):
        expected = q * p if q is not None and p is not None else None
        delta = t - expected if expected is not None and t is not None else None
        total_calculado.append(expected)
        diferenca.append(delta)
        divergencia.append(int(delta is not None and abs(delta) > Decimal('0.01')))
    df['preco_total_calculado'] = total_calculado
    df['diferenca_total'] = diferenca
    df['flag_total_divergente'] = divergencia
    df['flag_quantidade_nao_positiva'] = df['quantidade'].map(lambda x: x is not None and x <= 0).astype('int8')
    df['flag_preco_negativo'] = df['preco_unitario'].map(lambda x: x is not None and x < 0).astype('int8')
    df['flag_total_negativo'] = df['preco_total'].map(lambda x: x is not None and x < 0).astype('int8')
    df['faixa_quantidade'] = pd.cut(df['quantidade'].map(lambda x: float(x) if x is not None else float('nan')),
        bins=[0,100,1000,10000,100000,float('inf')],labels=['01: 1–100','02: >100–1.000','03: >1.000–10.000','04: >10.000–100.000','05: >100.000']).astype('string')
    necessary = ['codigo_catmat','descricao_produto','unidade_apresentacao','fabricante_id','uf','modalidade_compra','data_compra']
    df['elegivel_preco'] = (df[necessary].notna().all(axis=1)
        & df['quantidade'].map(lambda x: x is not None and x > 0)
        & df['preco_unitario'].map(lambda x: x is not None and x > 0)
        & df['preco_total'].map(lambda x: x is not None and x > 0)
        & df['flag_total_divergente'].eq(0)
        & df['flag_ano_data_divergente'].eq(0)
        & df['flag_data_futura'].eq(0)).astype('int8')
    return df, changes, audit_samples

