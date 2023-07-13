from frictionless import Step, Package, Resource, transform, steps, Field
from pathlib import Path
from .utils import as_identifier
import attrs

class field_rename_to_target(Step):
    def transform_resource(self, resource: Resource):
        resource.schema.primary_key = []
        resource.schema.foreign_keys = []
        for field in resource.schema.fields:
            if not field.custom.get('target'):
                field.custom['target'] = as_identifier(field.name)
            target = field.custom['target']
            descriptor = {'name': target, 'source': field.name}
            resource.schema.update_field(field.name, descriptor)
            resource.schema.get_field(target).custom.pop('target')

@attrs.define(kw_only=True, repr=False)
class table_write_normalized(Step):
    """
    Class docstring
    """
    
    path: str
    """
    resource.path for the new normalized resource
    """

    def transform_resource(self, resource: Resource):
        
        transform(resource, steps=[steps.table_normalize()])
        path = Path(self.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        resource.to_petl().tocsv(path, encoding = 'utf-8')
        resource.profile = 'tabular-data-resource'
        resource.data = None
        resource.path = self.path
        resource.encoding = 'utf-8'
        resource.format = 'csv'
        resource.scheme = 'file'
        resource.extrapaths = None
        for field in resource.schema.fields:
            field.format = None
            field.missing_values = None
            field.true_values = None
            field.false_values = None
            field.group_char = None
            field.decimal_char = None
            field.bare_number = None
