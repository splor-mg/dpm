from datetime import datetime
from pathlib import Path
import pandas as pd
from frictionless import Package, Resource



def concat(*packages, resource_name, id_cols = None):
    """
    >>> indicadores = concat(sigplan2024, sigplan2023, resource_name = 'indicadores_planejamento', id_cols={'ano': 'period'})
    """

    resources = []
    all_columns = set()
    
    # First pass to collect all unique columns
    for package in packages:
        resource = package[resource_name]
        all_columns.update(resource.columns)

    # Second pass to ensure all DataFrames have all columns
    for package in packages:
        resource = package[resource_name]
        # Add missing columns with NaN values
        for col in all_columns:
            if col not in resource.columns:
                resource[col] = pd.NA
                
        if id_cols and isinstance(id_cols, dict):
            for key, value in id_cols.items():
                if hasattr(package._package, value):
                    resource[key] = getattr(package._package, value)
                else:
                    resource[key] = getattr(package._package, 'custom')[value]
        resources.append(resource)
    
    return pd.concat(resources, ignore_index=True)


def chunk_concat_and_write(*packages, resource_name, id_cols=None, output_file='output.csv', chunksize=10000):
    """
    Concatenate large datapackages without loading all data into memory.
    Writes data in chunks directly to disk.
    """
    # First pass to collect all unique columns
    all_columns = set()
    for package in packages:
        resource_path = Path(package.basepath, package.get_resource(resource_name).path)
        # Read just the header to get column names
        df_header = pd.read_csv(resource_path, nrows=0)
        all_columns.update(df_header.columns)

    # writes the header only once
    header_written = False

    for package in packages:
        resource_path = Path(package.basepath, package.get_resource(resource_name).path)
        # Read each resource in chunks
        for chunk in pd.read_csv(resource_path, chunksize=chunksize):
            # Add missing columns with NaN values
            for col in all_columns:
                if col not in chunk.columns:
                    chunk[col] = pd.NA

            if id_cols and isinstance(id_cols, dict):
                for key, value in id_cols.items():
                    if hasattr(package, value):
                        chunk[key] = getattr(package, value)
                    else:
                        chunk[key] = getattr(package, 'custom')[value]

            # Write each chunk to the output file, appending after the first chunk
            chunk.to_csv(output_file, mode='a', header=not header_written, index=False, encoding='utf-8')
            header_written = True


def build_package(data_files: list, package_name: Path, output_dir: Path):

    """
        Create datapackage.json for the concatenated resources
    """

    package = Package()
    package.name = package_name

    # Add each file as a resource
    for file_path in data_files:

        resource = Resource.describe(Path(output_dir, file_path.name))
        resource.infer(stats=True)
        resource.profile = "tabular-data-resource"
        package.add_resource(resource)
        resource.path = str((output_dir.relative_to(output_dir.parent) / f'{resource.name}.csv').as_posix())

    package.profile = "tabular-data-package"
    package.custom['updated_at'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    package.to_json(Path(output_dir.parent, 'datapackage.json'))