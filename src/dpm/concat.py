from pathlib import Path
import pandas as pd


def concat(*packages, resource_name, id_cols = None):
    """
    >>> indicadores = concat(sigplan2024, sigplan2023, resource_name = 'indicadores_planejamento', id_cols={'ano': 'period'})
    """

    resources = []
    for package in packages:
        resource = package[resource_name]
        if id_cols and isinstance(id_cols, dict):
            for key, value in id_cols.items():
                if hasattr(package._package, value):
                    resource[key] = getattr(package._package, value)
                else:
                    resource[key] = getattr(package._package, 'custom')[value]
        resources.append(resource)
    return pd.concat(resources, ignore_index = True)


def chunk_concat_and_write(*packages, resource_name, id_cols=None, output_file='output.csv', chunksize=10000):
    """
    Concatenate large datapackages without loading all data into memory.
    Writes data in chunks directly to disk.
    """
    # writes the header only once
    header_written = False

    for package in packages:
        resource_path = Path(package.basepath, package.get_resource(resource_name).path)
        # Read each resource in chunks
        for chunk in pd.read_csv(resource_path, chunksize=chunksize):
            if id_cols and isinstance(id_cols, dict):
                for key, value in id_cols.items():
                    if hasattr(package._package, value):
                        chunk[key] = getattr(package._package, value)
                    else:
                        chunk[key] = getattr(package._package, 'custom')[value]

            # Write each chunk to the output file, appending after the first chunk
            chunk.to_csv(output_file, mode='a', header=not header_written, index=False, encoding='utf-8')
            header_written = True