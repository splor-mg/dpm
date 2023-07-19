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
            steps.table_normalize(),
            steps.row_filter(formula='uo_cod != 1251'),
        ],
    )
    resource.transform(pipeline)
    assert len(resource.read_rows()) == 2
