from decimal import Decimal
import pandas as pd
from src.clean_data import decimal_value, normalize_text, identity, clean_frame, COLUMN_MAP

def test_decimal_locale_and_zero():
    assert decimal_value('1.234,50') == Decimal('1234.50')
    assert decimal_value('0.0001') == Decimal('0.0001')
    assert decimal_value('0') == Decimal('0')
    assert decimal_value('') is None
    assert decimal_value('1,234,50') is None
    assert decimal_value('NaN') is None
    assert decimal_value('-2') == Decimal('-2')

def test_weighted_price_is_not_arithmetic_mean():
    quantities=[Decimal('10'),Decimal('90')]
    prices=[Decimal('2'),Decimal('4')]
    assert sum(q*p for q,p in zip(quantities,prices))/sum(quantities) == Decimal('3.8')
    assert sum(prices)/2 == Decimal('3')

def test_accents_and_cnpj_leading_zero():
    assert normalize_text('  SAU\u0301DE\n PÚBLICA ') == 'SAÚDE PÚBLICA'
    ids=identity(pd.Series(['01234567000189','00000000000000',None],dtype='string'),pd.Series(['A','B',None],dtype='string'))
    assert ids.iloc[0]=='01234567000189'
    assert ids.iloc[1]=='NOME:B'
    assert pd.isna(ids.iloc[2])

def test_bad_values_and_duplicates_preserved():
    row={c:'' for c in COLUMN_MAP}
    row.update(ano_compra='2020',dt_compra='31/02/2020',dt_insercao='01/03/2020',
        qt_medicamento='-2',vl_preco_unitario='3',vl_preco_total='6')
    raw=pd.DataFrame([row,row],dtype='string')
    df,_,_=clean_frame(raw,2020)
    assert len(df)==2
    assert df['registro_id'].nunique()==2
    assert df['flag_invalido_data_compra'].sum()==2
    assert df['flag_quantidade_nao_positiva'].sum()==2
    assert df['flag_total_divergente'].sum()==2
    assert df['elegivel_preco'].sum()==0

