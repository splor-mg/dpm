from dpm.utils import as_identifier

def test_as_identifier_upper():
    x = 'valor (r$) 2024'
    result = as_identifier(x)
    assert result == 'valor_2024'

def test_as_identifier_lower():
    x = ' Unidade Orçamentária - Código '
    result = as_identifier(x, case=str.upper)
    assert result == 'UNIDADE_ORCAMENTARIA_CODIGO'
