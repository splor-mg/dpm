from frictionless import Package, Resource, Pipeline, steps
from datetime import datetime
import petl as etl
from pathlib import Path
from .utils import as_identifier

def normalize_resource(resource: Resource, data_dir: Path):
    
    transform_pipeline = Pipeline(steps=[
    steps.table_normalize(),
    ])

    resource.transform(transform_pipeline)
    table = resource.to_petl()
    for field in resource.schema.fields:
        target = field.custom.get('target')
        target = target if target else as_identifier(field.name)
        table = etl.rename(table, field.name, target)
    etl.tocsv(table, data_dir / f'{resource.name}.csv', encoding='utf-8')

def normalize_package(package: Package, output_dir: Path, data_dir: Path):
    
    descriptor = {
        "profile": "tabular-data-package",
        "name": package.name,
        "resources": [
            {
            "profile": "tabular-data-resource",
            "name": resource_name,
            "path": str(data_dir / f'{resource_name}.csv'),
            "format": "csv",
            "encoding": "utf-8",
            "schema": {"fields": [
                {
                'name': field.custom['target'] if field.custom.get('target') else as_identifier(field.name),
                'type': field.type,
                'source': field.name,
                } for field in package.get_resource(resource_name).schema.fields                
            ]}
            } for resource_name in package.resource_names
        ]
    }

    target = Package.from_descriptor(descriptor)
    target.custom['updated_at'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    for resource in target.resources:
        resource.infer(stats=True)

    target.to_json(output_dir / 'datapackage.json')
