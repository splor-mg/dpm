from frictionless import Resource
from dpm.steps import normalize_resource
from datetime import date, datetime

def test_resource_normalize():
    resource = Resource('tests/data/temporal-dim.yaml')
    descriptor = normalize_resource(resource, 'tests/data/normalize_resource_output.csv').to_descriptor()
    target = Resource.from_descriptor(descriptor)
    
    assert descriptor == {'name': 'temporal-dim',
                          'type': 'table',
                          'profile': 'tabular-data-resource',
                          'path': 'tests/data/normalize_resource_output.csv',
                          'scheme': 'file',
                          'format': 'csv',
                          'mediatype': 'text/csv',
                          'encoding': 'utf-8',
                          'schema': {'fields': [{'name': 'uo_cod',
                                                  'type': 'integer',
                                                  'constraints': {'required': True},
                                                  'source': 'Unidade Orçamentária - Código'},
                                              {'name': 'UO_DESC',
                                                  'type': 'string',
                                                  'source': 'uo_desc'},
                                              {'name': 'valid',
                                                  'type': 'boolean',
                                                  'source': 'Vigente?'},
                                              {'name': 'VALID_FROM',
                                                  'type': 'date',
                                                  'source': 'VALID_FROM'},
                                              {'name': 'VALID_TO',
                                                  'type': 'date',
                                                  'description': 'This is a big and nice description\n',
                                                  'source': 'Valid_to'},
                                              {'name': 'UPDATED_AT',
                                                  'type': 'datetime',
                                                  'source': 'Updated at'}],
                                      'primaryKey': ['uo_cod', 'VALID_FROM', 'VALID_TO']}}
    assert target.read_rows() == [
    {'uo_cod': 1501, 'UO_DESC': 'Planejamento e Gestão', 'valid': False, 'VALID_FROM': date(1995, 1, 1), 'VALID_TO': date(2002, 1, 1), 'UPDATED_AT': datetime(1994, 11, 30, 9, 45)}, 
    {'uo_cod': 1501, 'UO_DESC': 'SEPLAG', 'valid': True, 'VALID_FROM': date(2002, 1, 1), 'VALID_TO': date(9999, 12, 31), 'UPDATED_AT': datetime(2002, 9, 30, 10, 45)}, 
    {'uo_cod': 1251, 'UO_DESC': None, 'valid': True, 'VALID_FROM': date(2002, 1, 1), 'VALID_TO': date(9999, 12, 31), 'UPDATED_AT': datetime(2002, 9, 30, 10, 45)}, 
    {'uo_cod': 1251, 'UO_DESC': 'PMMG', 'valid': True, 'VALID_FROM': date(2002, 1, 1), 'VALID_TO': date(9999, 12, 31), 'UPDATED_AT': datetime(2002, 9, 30, 10, 43)}
]
