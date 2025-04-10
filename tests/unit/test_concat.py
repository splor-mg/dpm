from cgi import test
import pytest
import pandas as pd
from pathlib import Path
from frictionless import Package, Resource
from dpm.utils import read_datapackage
from dpm.concat import concat, chunk_concat_and_write 

@pytest.fixture
def sample_packages_fric():
    # Sample Frictionless Packages
    sigplan2024 = Package("tests/data/datapackages/siafi_2024/datapackage.json")
    sigplan2025 = Package("tests/data/datapackages/siafi_2025/datapackage.json")
  
    return sigplan2024, sigplan2025


@pytest.fixture
def sample_packages_read():
    
    # load Sample Frictionless Packages
    
    sigplan2024 = read_datapackage("tests/data/datapackages/siafi_2024/datapackage.json")
    sigplan2025 = read_datapackage("tests/data/datapackages/siafi_2025/datapackage.json")
    
    return sigplan2024, sigplan2025


def test_concat(sample_packages_read):
    sigplan2024, sigplan2025 = sample_packages_read
    result = concat(sigplan2024, sigplan2025, resource_name="execucao")

    # Verify the resulting DataFrame
    assert isinstance(result, pd.DataFrame)
    # Combined rows from both packages
    assert result.shape[0] == 22  # Sum of rows from 2024 and 2025 execucao
    # Verify columns match the schema
    assert result.shape[1] == 30  # Number of fields in execucao schema
    # Verify key columns exist


def test_concat_with_id_cols(sample_packages_read):
    sigplan2023, sigplan2024 = sample_packages_read
    id_cols = {"atualizado_em": "updated_at"}

    result = concat(sigplan2023, sigplan2024, resource_name="execucao", id_cols=id_cols)

    # Verify new column and content
    assert "atualizado_em" in result.columns
    assert set(result["atualizado_em"].tolist()) == set(["2025-03-03T10:17:16", "2025-01-30T18:26:55"])

def test_chunk_concat_and_write(tmp_path, sample_packages_fric):
    print(tmp_path)
    sigplan2024, sigplan2025 = sample_packages_fric
    output_file = tmp_path / "output.csv"
    chunk_concat_and_write(sigplan2024, sigplan2025, resource_name="execucao", output_file=str(output_file), chunksize=1)

    
    assert output_file.exists()

    data = pd.read_csv(output_file)
    assert data.shape == (22, 30)  # Expecting 22 rows and 30 columns


