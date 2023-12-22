from typer.testing import CliRunner
from dpm.cli import app


runner = CliRunner()

def test_app(tmp_path):
        result = runner.invoke(app, ['install', 'tests/data/data.toml', '--output-dir', str(tmp_path)])
        expected_files = sorted([
                                tmp_path / 'reprex-excel',
                                tmp_path / 'transparencia-reprex-foreignkey',
                                tmp_path / 'reprex-excel/missing_date.xlsx',
                                tmp_path / 'reprex-excel/datapackage.json',
                                tmp_path / 'reprex-excel/missing_date.csv',
                                tmp_path / 'transparencia-reprex-foreignkey/datapackage.json',
                                tmp_path / 'transparencia-reprex-foreignkey/data',
                                tmp_path / 'transparencia-reprex-foreignkey/data/estados.csv',
                                tmp_path / 'transparencia-reprex-foreignkey/data/pib-per-capita.csv'])

        files = sorted(tmp_path.glob('**/*'))

        assert result.exit_code == 0
        assert expected_files == files
