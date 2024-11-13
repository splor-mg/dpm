import pytest
import pandas as pd
from pathlib import Path
from frictionless import Package, Resource
from my_module import concat, chunk_concat_and_write  # Adjust 'my_module' to the actual module name

@pytest.fixture
def sample_packages():
    # Sample Frictionless Packages
    sigplan2023 = Package(resources=[Resource(name="indicadores_planejamento", data=[
        {"id": 1, "name": "A", "value": 100},
        {"id": 2, "name": "B", "value": 200}
    ])])

    sigplan2024 = Package(resources=[Resource(name="indicadores_planejamento", data=[
        {"id": 3, "name": "C", "value": 300},
        {"id": 4, "name": "D", "value": 400}
    ])])

    return sigplan2023, sigplan2024

def test_concat(sample_packages):
    sigplan2023, sigplan2024 = sample_packages
    result = concat(sigplan2023, sigplan2024, resource_name="indicadores_planejamento")

    # Verify the resulting DataFrame
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (4, 3)  # Expecting 4 rows and 3 columns
    assert result['id'].tolist() == [1, 2, 3, 4]
    assert result['value'].sum() == 1000

def test_concat_with_id_cols(sample_packages):
    sigplan2023, sigplan2024 = sample_packages
    id_cols = {"ano": "custom_period"}

    # Add custom period to mock packages
    sigplan2023.custom = {"custom_period": 2023}
    sigplan2024.custom = {"custom_period": 2024}
    sigplan2024.custom = {"custom_period": 2024}

    result = concat(sigplan2023, sigplan2024, resource_name="indicadores_planejamento", id_cols=id_cols)

    # Verify new column and content
    assert "ano" in result.columns
    assert result["ano"].tolist() == [2023, 2023, 2024, 2024]

def test_chunk_concat_and_write(tmp_path, sample_packages):
    sigplan2023, sigplan2024 = sample_packages
    output_file = tmp_path / "output.csv"
    chunk_concat_and_write(sigplan2023, sigplan2024, resource_name="indicadores_planejamento", output_file=str(output_file), chunksize=1)

    # Check if file exists and is not empty
    assert output_file.exists()
    data = pd.read_csv(output_file)
    assert data.shape == (4, 3)  # Expecting 4 rows and 3 columns
    assert data['value'].sum() == 1000
