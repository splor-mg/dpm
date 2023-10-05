from typer.testing import CliRunner
from dpm.cli import app

runner = CliRunner()

def test_app(tmp_path):
        result = runner.invoke(app, ['install', 'tests/data/data.toml', '--output-dir', str(tmp_path)])
        expected_files = [f'{str(tmp_path)}/reprex-excel', 
                          f'{str(tmp_path)}/transparencia-reprex-foreignkey', 
                          f'{str(tmp_path)}/reprex-excel/missing_date.xlsx', 
                          f'{str(tmp_path)}/reprex-excel/datapackage.json', 
                          f'{str(tmp_path)}/reprex-excel/missing_date.csv', 
                          f'{str(tmp_path)}/transparencia-reprex-foreignkey/datapackage.json', 
                          f'{str(tmp_path)}/transparencia-reprex-foreignkey/data', 
                          f'{str(tmp_path)}/transparencia-reprex-foreignkey/data/estados.csv', 
                          f'{str(tmp_path)}/transparencia-reprex-foreignkey/data/pib-per-capita.csv']
        files = [str(file) for file in tmp_path.glob('**/*')]
        assert result.exit_code == 0
        assert expected_files == files
