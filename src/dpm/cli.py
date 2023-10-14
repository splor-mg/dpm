import typer
from typing_extensions import Annotated
from frictionless import Package
from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from dpm.install import extract_source_packages
from dpm.load import read_manifest, load_package, create_if_not_exists_control_table

app = typer.Typer()

@app.callback()
def callback():
    """
    Data package manager to install, update and remove data dependencies.
    """

@app.command()
def install(descriptor: Annotated[Path, typer.Argument()] = Path('data.toml'),
            output_dir: Annotated[Path, typer.Option()] = Path('datapackages')):
    """
    Download data packages (descriptor and resources data files) listed in package.sources and saves into datapackages/
    """
    with open(descriptor, "rb") as f:
        data_toml = tomllib.load(f)

    extract_source_packages(data_toml, output_dir)

@app.command()
def load():
    """
    Load data packages into database
    """
    create_if_not_exists_control_table()
    
    manifest = read_manifest('data.toml')

    for pkg_id in manifest['packages'].keys():
        path = Path('datapackages') / pkg_id / 'datapackage.json'
        package = Package(path)
        load_package(pkg_id, package)
