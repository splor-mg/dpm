from dpm.utils import as_identifier

def test_as_identifier_upper():
    x = 'valor (r$) 2024'
    result = as_identifier(x)
    assert result == 'VALOR_2024'

def test_as_identifier_lower():
    x = ' Unidade Orçamentária - Código '
    result = as_identifier(x, case=str.lower)
    assert result == 'unidade_orcamentaria_codigo'
