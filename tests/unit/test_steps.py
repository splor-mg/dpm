from frictionless import Resource, Schema, Pipeline, steps
from frictionless.resources import TableResource
from dpm.steps import field_rename_to_target

def test_step_field_rename_to_target():
    resource = Resource('tests/data/temporal-dim.yaml')
    
    pipeline = Pipeline(
        steps=[
            field_rename_to_target(),
        ],
    )
    resource.transform(pipeline)
    assert resource.schema.to_descriptor()['fields'] == [
            {'name': 'uo_cod', 'type': 'integer', 'constraints': {'required': True}, 'source': 'Unidade Orçamentária - Código'},
            {'name': 'uo_desc', 'type': 'string', 'source': 'uo_desc'},
            {'name': 'valid', 'type': 'boolean', 'trueValues': ['Sim'], 'falseValues': ['Não'], 'source': 'Vigente?'},
            {'name': 'valid_from', 'type': 'date', 'format': '%d/%m/%Y', 'source': 'VALID_FROM'},
            {'name': 'valid_to', 'type': 'date', 'description': 'This is a big and nice description\n', 'format': '%d/%m/%Y', 'source': 'Valid_to'},
            {'name': 'updated_at', 'type': 'datetime', 'format': '%d/%m/%Y %H:%M:%S', 'source': 'Updated at'}
        ]
    