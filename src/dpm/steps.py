from frictionless import Step, Package, Resource, transform, steps, Field, fields, Dialect
from pathlib import Path
from .utils import as_identifier, remove_field_properties
import attrs
import petl as etl

class field_rename_to_target(Step):
    """
    Rename a field to a target property if present or to a slugified version of current name preserving lineage through source property.

    Example:

        The source schema:
        
        ---
        fields:
            - name: Programa - Código
            target: programa_cod
            - name: Programa Desc
            - name: vr_meta_orcamentaria
        ...

        is converted to the target schema:
        
        ---
        fields:
            - name: programa_cod
            source: Programa - Código
            - name: programa_desc
            source: Programa Desc
            - name: vr_meta_orcamentaria
            source: vr_meta_orcamentaria
        ...
    """

    def transform_resource(self, resource: Resource):
        resource.schema.primary_key = []
        resource.schema.foreign_keys = []
        mapping = {}
        for field in resource.schema.fields:
            if not field.custom.get('target'):
                field.custom['target'] = as_identifier(field.name)
            target = field.custom['target']
            mapping[field.name] = target
            descriptor = {'name': target, 'source': field.name}
            resource.schema.update_field(field.name, descriptor)
            resource.schema.get_field(target).custom.pop('target')
        table = resource.to_petl()
        table = etl.rename(table, mapping)
        resource.data = table

@attrs.define(kw_only=True, repr=False)
class table_write_normalized(Step):
    """
    Normalize fields (number, integer, boolean, date, time, datetime) that allow variable formatting (eg. July 13, 2023 vs 2023-07-13) and missing values to a standard representation and export the data to a given path or to a given folder with filename resource-name.csv.

    The field descriptor is also adjusted so that it continues to be valid for the normalized data (ie. `"format": "%d/%m/%y"` no longer apply to a DateField after normalization and should be removed).

    The following properties are dropped if present:

    - `decimalChar`
    - `groupChar`
    - `bareNumber`
    - `trueValues`
    - `falseValues`
    - `format`
    - `missingValues`

    """
    
    path: str = None
    output_dir: str = None

    def transform_resource(self, resource: Resource):
        
        resource_copy = resource.to_copy()

        transform(resource_copy, steps=[steps.table_normalize()])
        if self.path is not None and self.output_dir is not None:
            raise ValueError("Only one of 'path' or 'output_dir' can be specified")
        if self.path is None and self.output_dir is None:
            raise ValueError("One of 'path' or 'output_dir' must be specified")
        if self.output_dir:
            path = Path(f'{self.output_dir}/{Path(resource.name).stem}.csv')
        else:
            path = Path(self.path)
        
        path.parent.mkdir(parents=True, exist_ok=True)
        resource_copy.to_petl().tocsv(path, encoding = 'utf-8')
        resource.path = str(path)
        resource.profile = 'tabular-data-resource'
        resource.encoding = 'utf-8'
        resource.format = 'csv'
        resource.dialect = Dialect()
        resource.scheme = 'file'
        for field in resource.schema.fields:
            if isinstance(field, fields.NumberField):
                resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues', 'groupChar', 'decimalChar', 'bareNumber'])
            elif isinstance(field, fields.BooleanField):
                resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues', 'trueValues', 'falseValues'])
            elif isinstance(field, fields.IntegerField):
                resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues', 'bareNumber'])
            elif isinstance(field, fields.DateField):
                resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues', 'format'])
            elif isinstance(field, fields.TimeField):
                resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues', 'format'])
            elif isinstance(field, fields.DatetimeField):
                resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues', 'format'])
            else:
                resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues'])

def normalize_resource(resource, path):

    resource = resource.to_copy()
    path = Path(path)
    
    for field in resource.schema.fields:
        if not field.custom.get('target'):
            field.custom['target'] = as_identifier(field.name)
        target = field.custom['target']
        field_descriptor = {'name': target, 'source': field.name}
        transform(resource, steps=[steps.field_update(name = field.name, descriptor = field_descriptor)])
        resource.schema.get_field(target).custom.pop('target')
    
    transform(resource, steps=[steps.table_normalize()])
    
    path.parent.mkdir(parents=True, exist_ok=True)
    resource.to_petl().tocsv(path, encoding = 'utf-8')
    
    resource.path = str(path)
    resource.profile = 'tabular-data-resource'
    resource.encoding = 'utf-8'
    resource.format = 'csv'
    for field in resource.schema.fields:
        if isinstance(field, fields.NumberField):
            resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues', 'groupChar', 'decimalChar', 'bareNumber'])
        elif isinstance(field, fields.BooleanField):
            resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues', 'trueValues', 'falseValues'])
        elif isinstance(field, fields.IntegerField):
            resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues', 'bareNumber'])
        elif isinstance(field, fields.DateField):
            resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues', 'format'])
        elif isinstance(field, fields.TimeField):
            resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues', 'format'])
        elif isinstance(field, fields.DatetimeField):
            resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues', 'format'])
        else:
            resource.schema = remove_field_properties(resource.schema, field.name, ['missingValues'])
    
    resource_descriptor = resource.to_descriptor()
    resource_descriptor.pop('data', None)
    resource_descriptor.pop('extrapaths', None)
    resource_descriptor.pop('dialect', None)
    return Resource.from_descriptor(resource_descriptor)
