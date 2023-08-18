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
                                              {'name': 'uo_desc',
                                                  'type': 'string',
                                                  'source': 'uo_desc'},
                                              {'name': 'valid',
                                                  'type': 'boolean',
                                                  'source': 'Vigente?'},
                                              {'name': 'valid_from',
                                                  'type': 'date',
                                                  'source': 'VALID_FROM'},
                                              {'name': 'valid_to',
                                                  'type': 'date',
                                                  'description': 'This is a big and nice description\n',
                                                  'source': 'Valid_to'},
                                              {'name': 'updated_at',
                                                  'type': 'datetime',
                                                  'source': 'Updated at'}],
                                      'primaryKey': ['uo_cod', 'valid_from', 'valid_to']}}
    assert target.read_rows() == [
    {'uo_cod': 1501, 'uo_desc': 'Planejamento e Gestão', 'valid': False, 'valid_from': date(1995, 1, 1), 'valid_to': date(2002, 1, 1), 'updated_at': datetime(1994, 11, 30, 9, 45)}, 
    {'uo_cod': 1501, 'uo_desc': 'SEPLAG', 'valid': True, 'valid_from': date(2002, 1, 1), 'valid_to': date(9999, 12, 31), 'updated_at': datetime(2002, 9, 30, 10, 45)}, 
    {'uo_cod': 1251, 'uo_desc': None, 'valid': True, 'valid_from': date(2002, 1, 1), 'valid_to': date(9999, 12, 31), 'updated_at': datetime(2002, 9, 30, 10, 45)}, 
    {'uo_cod': 1251, 'uo_desc': 'PMMG', 'valid': True, 'valid_from': date(2002, 1, 1), 'valid_to': date(9999, 12, 31), 'updated_at': datetime(2002, 9, 30, 10, 43)}
]
