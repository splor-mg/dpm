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
                    resource[key] = getattr(package._package, 'custom').get(value)
        resources.append(resource)
    return pd.concat(resources, ignore_index = True)
