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
        print(f"ERROR: Path is missing filename: {path}")
        return False

    # Check if it has an extension
    if path.suffix == '':
        print(f"ERROR: Path is missing file extension: {path}")
        return False

    return True

def read_jsonlines(logfile_path):
    """
    Read JSON Lines file and return DataFrame
    """
    if logfile_path.exists():
        return pd.read_json(logfile_path, lines=True)
    else:
        print(f"ERROR: Log file does not exist: {logfile_path}. Please check the path and try again.")
        exit(0)


def filter_jsonlines(df, filter_key, filter_value):
    """
    Filter the DataFrame based on a specific key and value
    """
    if filter_value in df.type.values:
        return df[df[filter_key] == filter_value]
    else:
        print(f"ERROR: The test {filter_value} is not present in the log file. Please check the test name and try again")
        exit(1)

def jsonlog_toexcel(df, output_dir: Path):
    """
    Convert Jsonlines DataFrame to an Excel file with multiple sheets for each 'type' of test,
    only including the relevant columns from the 'row' dictionary for each type.
    """
    test_number = 1

    # Group by 'type' and create a new sheet for each group
    with pd.ExcelWriter(output_dir, engine='openpyxl') as writer:
        for test_type, group_df in df.groupby('type'):

            # Expand the 'row' column dictionary into separate columns for the current group
            row_df = pd.json_normalize(group_df['row'])

            # Filter the columns of 'row' that are not null, avoiding writing columns that not belong to a given test
            relevant_columns = row_df.columns[row_df.notnull().any()].tolist()

            # Combine 'test_type', 'message', and the relevant expanded 'row' columns
            final_df = pd.DataFrame({
                'type': test_type,
                'message': group_df['message'].values
            })

            # Add relevant columns from the expanded row_df
            for col in relevant_columns:
                final_df[col] = row_df[col].values

            # Replace '=' with "'=" in string columns to avoid excel formula dectetion errors
            final_df = final_df.map(lambda x: str(x).replace('=', "'=") if isinstance(x, str) else x)

            final_df.to_excel(writer, sheet_name=f"teste_{test_number}", index=False)

            test_number += 1
