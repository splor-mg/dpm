from typer.testing import CliRunner
from dpm.cli import app

runner = CliRunner()

def test_normalize_package_json(snapshot):
    result = runner.invoke(
        app,
        [
            "normalize", "tests/data/datapackage.yaml",
            "--metadata-dir", "tests/data",
            "--data-dir", "tests/data/data-raw",
        ],
    )
    assert result.output == snapshot

def test_normalize_package_yaml(snapshot):
    result = runner.invoke(
        app,
        [
            "normalize", "tests/data/datapackage.yaml", "--yaml",
            "--metadata-dir", "tests/data",
            "--data-dir", "tests/data/data-raw",
        ],
    )
    assert result.output == snapshot

def test_normalize_resource_json(snapshot):
    result = runner.invoke(
        app,
        [
            "normalize", "tests/data/datapackage.yaml",
            "--metadata-dir", "tests/data",
            "--data-dir", "tests/data/data-raw",
            "--resource-name", "temporal-dim",
        ],
    )
    assert result.output == snapshot
