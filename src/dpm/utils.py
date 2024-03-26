import re
from unidecode import unidecode
from frictionless import Schema, Package
import json
from pathlib import Path

def as_identifier(x, case=str.lower): 
    result = unidecode(x) 
    result = re.sub(r'\([^)]*\)', '', result)  # Remove all characters within parentheses
    result = result.replace('\u00a0', ' ')  # Replace non-breaking space with regular space
    result = re.sub('\W|^(?=\d)','_', result)
    result = re.sub('_+', '_', result)
    result = case(result)
    return result.strip('_')

def remove_field_properties(schema, field_name, properties):
    schema_descriptor = schema.to_descriptor()
    field_descriptor = schema.get_field(field_name).to_descriptor()
    
    for property in properties:
        field_descriptor.pop(property, None)
        
    schema_descriptor['fields'] = [
        field_descriptor if field['name'] == field_name else field 
        for field in schema_descriptor['fields']
    ]

    return Schema.from_descriptor(schema_descriptor)

class read_datapackage:
    """
    Read all package resource to memory as pandas data frames

    >>> dp = read_datapackage('datapackage.json')
    >>> dp.my_resource
    >>> dp['my_resource']
    """
    def __init__(self, source):
        self._package = Package(source)
        for resource_name in self._package.resource_names:
            setattr(self, resource_name, self._package.get_resource(resource_name).to_pandas())
    def __getitem__(self, item):
        return getattr(self, item)
    def __repr__(self):
        return f"Package {self._package.name} ({len(self._package.resources)} resources)"

def add_metadata_to_json(resource_name, key, value, ):
    """
    Adds the pair key:value to the file logs/{resource_name}.json. Creates the file if it does not exist.

    Parameters
    ----------
    resource_name : str
        name of the file to be created or metadata appended.
    key : str
        Property key inserted in json.
    value : any
        Property value inserted into json.
    """
    file_path = Path(f'logs/{resource_name}.json')

    if Path.exists(file_path):
        with open(file_path, 'r') as file:
            # Load existing content
            metadata = json.load(file)
    else:
        metadata = {}

    metadata[key] = value

    with open(file_path, 'w') as file:
        json.dump(metadata, file, indent=2)


def write_dict_to_json(resource_name, data):
    """
    Saves the `data` dictionary as a JSON file `logs/{resource_name}.json. Replaces the file if it already exists.

    Parameters
    ----------
    resource_name : str
        The name of the resource to create a json metadata file.
    data : dict
        the dictionary that will be saved as JSON.
    """
    filepath = f'logs/{resource_name}.json'
    with open(filepath, 'w') as json_file:
        json.dump(data, json_file, indent=2, sort_keys=False)

