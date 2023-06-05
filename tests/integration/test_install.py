from typer.testing import CliRunner
from dpm.cli import app
from pathlib import Path

runner = CliRunner()

def test_app():
    result = runner.invoke(app, ["install", "--descriptor", "data/datapackage.yaml"])
    expected = ['datapackages/reprex-excel', 
                'datapackages/transparencia-reprex-foreignkey', 
                'datapackages/reprex-excel/missing_date.xlsx', 
                'datapackages/reprex-excel/datapackage.json', 
                'datapackages/reprex-excel/missing_date.csv', 
                'datapackages/transparencia-reprex-foreignkey/datapackage.json', 
                'datapackages/transparencia-reprex-foreignkey/data', 
                'datapackages/transparencia-reprex-foreignkey/data/estados.csv', 
                'datapackages/transparencia-reprex-foreignkey/data/pib-per-capita.csv']
    result = [str(file) for file in Path('datapackages').glob('**/*')]
    
    assert expected == result
