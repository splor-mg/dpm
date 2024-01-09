from frictionless import Package
from deepdiff import DeepDiff
from rich import print as rprint
import daff

def diff_schema(source, target, resource_name):
    source_resource = source.get_resource(resource_name)
    target_resource = target.get_resource(resource_name)

    source_fields = [field.name for field in source_resource.schema.fields]
    target_fields = [field.name for field in target_resource.schema.fields]

    diff = DeepDiff(source_fields, target_fields)

    if diff:
        schema_diff = daff.diff([source_fields], [target_fields])
        renderer = daff.TerminalDiffRender()
        print(renderer.render(schema_diff))
        return(1)
    else:
        print('No diff between objects.')
        return(0)
