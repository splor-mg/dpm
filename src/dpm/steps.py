from frictionless import Step, Package, Resource, transform, steps, Field
from pathlib import Path
from .utils import as_identifier
import attrs

class normalize_field_names(Step):
    def transform_resource(self, resource: Resource):
        resource.schema.primary_key = []
        resource.schema.foreign_keys = []
        for field in resource.schema.fields:
            target = field.custom.get('target')
            if target:
                descriptor = {'name': target, 'source': field.name}
                resource.schema.update_field(field.name, descriptor)
                resource.schema.get_field(target).custom.pop('target')
            elif field.name != as_identifier(field.name):
                resource.schema.update_field(field.name, {'name': as_identifier(field.name), 'source': field.name})


@attrs.define(kw_only=True, repr=False)
class enrich_resource(Step):
    
    classificacao: str
    key: str
    column: list

    def non_equi_join(self, x, y, key, key_y, column):
        """
        non_equi_join(fact, dim, 'code', 'code')
        """
        for row in x:
            matched = False
            for row_y in y:
                # print(f'{row=}')
                # print(f'{row_y=}')
                if row[key] == row_y[key_y] and row_y['valid_from'] <= row['valid_ref'] <= row_y['valid_to']:
                    desc = {column[1]: row_y[column[0]]}
                    yield {**row, **desc}
                    matched = True
                    break
            if not matched:
                    desc = {column[1]: None}
                    yield {**row, **desc}
    
    def transform_resource(self, resource: Resource):
        classificador = Package('https://raw.githubusercontent.com/splor-mg/classificador/dev/data/datapackage.json')
        result = self.non_equi_join(resource.read_rows(), classificador.get_resource(self.classificacao).read_rows(), self.key, 'code', self.column)
        resource.data = result
        resource.schema.add_field(Field.from_descriptor({'name': self.column[1], 'type': 'string'}), position=resource.schema.field_names.index(self.key)+2)

@attrs.define(kw_only=True, repr=False)
class normalize_resource_data(Step):
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
        resource.infer(stats=True)
        resource.dereference()
        for field in resource.schema.fields:
            field.format = None
            field.missing_values = None
            field.true_values = None
            field.false_values = None
            field.group_char = None
            field.decimal_char = None
            field.bare_number = None
