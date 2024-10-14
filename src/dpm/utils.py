import re
from pathlib import Path

from unidecode import unidecode
from frictionless import Schema, Package
import pandas as pd

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


def is_complete_path(path: Path) -> bool:
    """
    Check if the path contains a directory and a file name and extension
    """

    if path.name == '':
        print(f"Path is missing filename: {path}")
        return False

    # Check if it has an extension
    if path.suffix == '':
        print(f"Path is missing file extension: {path}")
        return False

    return True

def read_jsonlines(jsonl_file):
    """
    Read JSON Lines file and return DataFrame
    """
    return pd.read_json(jsonl_file, lines=True)


def filter_jsonlines(df, filter_key, filter_value):
    """
    Filter the DataFrame based on a specific key and value
    """
    return df[df[filter_key] == filter_value]


def jsonlog_toexcel(df, output_dir: Path):
    """
    Convert Jsonlines DataFrame to an Excel file
    """

    # Expand the 'row' column dictionary into separate columns
    row_df = pd.json_normalize(df['row'])

    # Combine 'message' and expanded 'row' columns
    # Ensure that the indices are properly aligned
    final_df = pd.concat([df[['message']].reset_index(drop=True), row_df.reset_index(drop=True)], axis=1)


    # Export the final DataFrame to Excel
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_excel(output_dir, index=False)
