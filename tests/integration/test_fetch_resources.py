from typer.testing import CliRunner
from dpm.cli import app


runner = CliRunner()

def test_app(tmp_path):
        result = runner.invoke(app, ['install', 'tests/data/fetch_resources.toml', '--output-dir', str(tmp_path)])
        expected_files = sorted([
                                tmp_path / 'obz-dados/data/misc/aux_agrupamento.xlsx',
                                tmp_path / 'obz-dados/data-raw/base_parecer_obz_dcmefo.xlsx',
                                tmp_path / 'obz-dados/data-raw/execucao_painel_obz.xlsx',
                                tmp_path / 'obz-dados/data-raw/uo_setor.xlsx',
                                tmp_path / 'obz-dados/datapackage.json',
                                tmp_path / 'reestimativa-dados/data/reest_rec.csv',
                                tmp_path / 'reestimativa-dados/datapackage.json',
                                tmp_path / 'sisor-dados-2024/data/base_categoria_pessoal.csv',
                                tmp_path / 'sisor-dados-2024/data/base_qdd_fiscal.csv',
                                tmp_path / 'sisor-dados-2024/datapackage.json',
                                tmp_path / 'teto-gastos-rrf-dados/datapackage.json'])

        files = sorted(tmp_path.glob('**/*'))

        assert result.exit_code == 0
        assert expected_files == files
