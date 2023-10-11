from typer.testing import CliRunner
from dpm.cli import app
from pathlib import Path

runner = CliRunner()


def test_app(tmp_path):
    result = runner.invoke(app, ['install', 'tests/data/fetch_resources.toml', '--output-dir',
                                 str(tmp_path)])
    expected_files = sorted([
        tmp_path / 'empty-fetch-list/datapackage.json',
        tmp_path / 'fetch-one-resource/data/estados.csv',
        tmp_path / 'fetch-one-resource/datapackage.json',
        tmp_path / 'invalid-fetch-only/datapackage.json',
        tmp_path / 'regular-install/data/estados.csv',
        tmp_path / 'regular-install/data/pib-per-capita.csv',
        tmp_path / 'regular-install/datapackage.json',
        tmp_path / 'valid-invalid-fetch/data/estados.csv',
        tmp_path / 'valid-invalid-fetch/datapackage.json',
    ])

    files = sorted(tmp_path.glob('**/*.*'))

    assert result.exit_code == 0
    assert expected_files == files
