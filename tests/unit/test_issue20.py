from frictionless import Resource, Pipeline, steps
from dpm.steps import field_rename_to_target, table_write_normalized
from datetime import date, datetime

def test_multiple_custom_steps(tmp_path):
    resource = Resource('tests/data/temporal-dim.yaml')
    
    output_dir = str(tmp_path / 'build')

    pipeline = Pipeline(
        steps=[
            field_rename_to_target(),
            table_write_normalized(output_dir=output_dir),
        ],
    )
    resource.transform(pipeline)
    assert resource.path == f'{output_dir}/{resource.name}.csv'
    assert resource.read_rows() == [
    {'uo_cod': 1501, 'uo_desc': 'Planejamento e Gestão', 'valid': False, 'valid_from': date(1995, 1, 1), 'valid_to': date(2002, 1, 1), 'updated_at': datetime(1994, 11, 30, 9, 45)}, 
    {'uo_cod': 1501, 'uo_desc': 'SEPLAG', 'valid': True, 'valid_from': date(2002, 1, 1), 'valid_to': date(9999, 12, 31), 'updated_at': datetime(2002, 9, 30, 10, 45)}, 
    {'uo_cod': 1251, 'uo_desc': None, 'valid': True, 'valid_from': date(2002, 1, 1), 'valid_to': date(9999, 12, 31), 'updated_at': datetime(2002, 9, 30, 10, 45)}, 
    {'uo_cod': 1251, 'uo_desc': 'PMMG', 'valid': True, 'valid_from': date(2002, 1, 1), 'valid_to': date(9999, 12, 31), 'updated_at': datetime(2002, 9, 30, 10, 43)}
]
