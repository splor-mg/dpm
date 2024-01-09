import pandas as pd

def concat(*packages, resource_name, id_col = None):
    """
    >>> indicadores = concat(sigplan2024, sigplan2023, resource_name = 'indicadores_planejamento', id_col={'ano': 'period'})
    """

    resources = []
    for package in packages:
        resource = package[resource_name]
        if id_col and isinstance(id_col, dict):
            for key, value in id_col.items():
                if hasattr(package._package, value):
                    resource[key] = getattr(package._package, value)
                else:
                    resource[key] = getattr(package._package, 'custom')[value]
        resources.append(resource)
    return pd.concat(resources, ignore_index = True)
