from frictionless import Resource, Schema, Pipeline, steps
from frictionless.resources import TableResource
from dpm.steps import field_rename_to_target, table_write_normalized
from datetime import date, datetime
from pathlib import Path

def test_step_field_rename_to_target():
    resource = Resource('tests/data/temporal-dim.yaml')
    
    pipeline = Pipeline(
        steps=[
            field_rename_to_target(),
        ],
    )
    resource.transform(pipeline)
    assert resource.path == 'data-raw/temporal-dim.txt'
    assert resource.schema.to_descriptor()['fields'] == [
            {'name': 'uo_cod', 'type': 'integer', 'constraints': {'required': True}, 'source': 'Unidade Orçamentária - Código'},
            {'name': 'uo_desc', 'type': 'string', 'missingValues': ['NA'] , 'source': 'uo_desc'},
            {'name': 'valid', 'type': 'boolean', 'trueValues': ['Sim'], 'falseValues': ['Não'], 'source': 'Vigente?'},
            {'name': 'valid_from', 'type': 'date', 'format': '%d/%m/%Y', 'source': 'VALID_FROM'},
            {'name': 'valid_to', 'type': 'date', 'description': 'This is a big and nice description\n', 'format': '%d/%m/%Y', 'source': 'Valid_to'},
            {'name': 'updated_at', 'type': 'datetime', 'format': '%d/%m/%Y %H:%M:%S', 'source': 'Updated at'}
        ]

def test_step_table_write_normalized(tmp_path):
    resource = Resource('tests/data/temporal-dim.yaml')
    
    path = str(tmp_path / 'data.csv')

    pipeline = Pipeline(
        steps=[
            table_write_normalized(path=path),
        ],
    )
    resource.transform(pipeline)
    target = Resource(path=path)
    
    assert resource.profile == 'tabular-data-resource'
    assert resource.format == 'csv'
    assert resource.scheme == 'file'
    assert resource.encoding == 'utf-8'
    assert resource.path
    assert isinstance(resource.path, str)
    
    assert resource.schema.to_descriptor()['fields'] == [
        {'name': 'Unidade Orçamentária - Código', 'type': 'integer', 'constraints': {'required': True}, 'target': 'uo_cod'}, 
        {'name': 'uo_desc', 'type': 'string'}, 
        {'name': 'Vigente?', 'type': 'boolean', 'target': 'valid'}, 
        {'name': 'VALID_FROM', 'type': 'date'}, 
        {'name': 'Valid_to', 'type': 'date', 'description': 'This is a big and nice description\n'}, 
        {'name': 'Updated at', 'type': 'datetime'}
    ]

    assert resource.read_rows() == [
        {'Unidade Orçamentária - Código': 1501, 'uo_desc': 'Planejamento e Gestão', 'Vigente?': False, 'VALID_FROM': date(1995, 1, 1), 'Valid_to': date(2002, 1, 1), 'Updated at': datetime(1994, 11, 30, 9, 45)}, 
        {'Unidade Orçamentária - Código': 1501, 'uo_desc': 'SEPLAG', 'Vigente?': True, 'VALID_FROM': date(2002, 1, 1), 'Valid_to': date(9999, 12, 31), 'Updated at': datetime(2002, 9, 30, 10, 45)}, 
        {'Unidade Orçamentária - Código': 1251, 'uo_desc': None, 'Vigente?': True, 'VALID_FROM': date(2002, 1, 1), 'Valid_to': date(9999, 12, 31), 'Updated at': datetime(2002, 9, 30, 10, 45)}, 
        {'Unidade Orçamentária - Código': 1251, 'uo_desc': 'PMMG', 'Vigente?': True, 'VALID_FROM': date(2002, 1, 1), 'Valid_to': date(9999, 12, 31), 'Updated at': datetime(2002, 9, 30, 10, 43)}
    ]

    assert target.read_rows() == [
        {'Unidade Orçamentária - Código': 1501, 'uo_desc': 'Planejamento e Gestão', 'Vigente?': False, 'VALID_FROM': date(1995, 1, 1), 'Valid_to': date(2002, 1, 1), 'Updated at': datetime(1994, 11, 30, 9, 45)}, 
        {'Unidade Orçamentária - Código': 1501, 'uo_desc': 'SEPLAG', 'Vigente?': True, 'VALID_FROM': date(2002, 1, 1), 'Valid_to': date(9999, 12, 31), 'Updated at': datetime(2002, 9, 30, 10, 45)}, 
        {'Unidade Orçamentária - Código': 1251, 'uo_desc': None, 'Vigente?': True, 'VALID_FROM': date(2002, 1, 1), 'Valid_to': date(9999, 12, 31), 'Updated at': datetime(2002, 9, 30, 10, 45)}, 
        {'Unidade Orçamentária - Código': 1251, 'uo_desc': 'PMMG', 'Vigente?': True, 'VALID_FROM': date(2002, 1, 1), 'Valid_to': date(9999, 12, 31), 'Updated at': datetime(2002, 9, 30, 10, 43)}
    ]

def test_step_table_write_normalized_output_dir(tmp_path):
    resource = Resource('tests/data/temporal-dim.yaml')
    
    output_dir = str(tmp_path / 'build')

    pipeline = Pipeline(
        steps=[
            table_write_normalized(output_dir=output_dir),
        ],
    )
    resource.transform(pipeline)
    target = Resource(path=f'{output_dir}/{Path(resource.name).stem}.csv')

    assert resource.path
    assert isinstance(resource.path, str)

    assert target.read_rows() == [
        {'Unidade Orçamentária - Código': 1501, 'uo_desc': 'Planejamento e Gestão', 'Vigente?': False, 'VALID_FROM': date(1995, 1, 1), 'Valid_to': date(2002, 1, 1), 'Updated at': datetime(1994, 11, 30, 9, 45)}, 
        {'Unidade Orçamentária - Código': 1501, 'uo_desc': 'SEPLAG', 'Vigente?': True, 'VALID_FROM': date(2002, 1, 1), 'Valid_to': date(9999, 12, 31), 'Updated at': datetime(2002, 9, 30, 10, 45)}, 
        {'Unidade Orçamentária - Código': 1251, 'uo_desc': None, 'Vigente?': True, 'VALID_FROM': date(2002, 1, 1), 'Valid_to': date(9999, 12, 31), 'Updated at': datetime(2002, 9, 30, 10, 45)}, 
        {'Unidade Orçamentária - Código': 1251, 'uo_desc': 'PMMG', 'Vigente?': True, 'VALID_FROM': date(2002, 1, 1), 'Valid_to': date(9999, 12, 31), 'Updated at': datetime(2002, 9, 30, 10, 43)}
    ]