from frictionless import Resource, transform
from dpm.steps import resource_normalize

resource = Resource('tests/data/temporal-dim.yaml')
transform(resource, steps=[resource_normalize(output_dir = 'data')])
descriptor = resource.to_descriptor()
Resource(descriptor)
