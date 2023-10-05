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
    {'uo_cod': 1501, 'UO_DESC': 'Planejamento e Gestão', 'valid': False, 'VALID_FROM': date(1995, 1, 1), 'VALID_TO': date(2002, 1, 1), 'UPDATED_AT': datetime(1994, 11, 30, 9, 45)}, 
    {'uo_cod': 1501, 'UO_DESC': 'SEPLAG', 'valid': True, 'VALID_FROM': date(2002, 1, 1), 'VALID_TO': date(9999, 12, 31), 'UPDATED_AT': datetime(2002, 9, 30, 10, 45)}, 
    {'uo_cod': 1251, 'UO_DESC': None, 'valid': True, 'VALID_FROM': date(2002, 1, 1), 'VALID_TO': date(9999, 12, 31), 'UPDATED_AT': datetime(2002, 9, 30, 10, 45)}, 
    {'uo_cod': 1251, 'UO_DESC': 'PMMG', 'valid': True, 'VALID_FROM': date(2002, 1, 1), 'VALID_TO': date(9999, 12, 31), 'UPDATED_AT': datetime(2002, 9, 30, 10, 43)}
]

def test_multiple_steps(tmp_path):
    resource = Resource('tests/data/temporal-dim.yaml')
    
    output_dir = str(tmp_path / 'build')

    pipeline = Pipeline(
        steps=[
            field_rename_to_target(),
            steps.row_filter(formula='UO_DESC == "PMMG"'),
            table_write_normalized(output_dir=output_dir),
        ],
    )
    resource.transform(pipeline)
    assert resource.path == f'{output_dir}/{resource.name}.csv'
    assert resource.read_rows() == [
    {'uo_cod': 1251, 'UO_DESC': 'PMMG', 'valid': True, 'VALID_FROM': date(2002, 1, 1), 'VALID_TO': date(9999, 12, 31), 'UPDATED_AT': datetime(2002, 9, 30, 10, 43)}
]
