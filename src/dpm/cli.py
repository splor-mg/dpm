import typer
import tomllib
from typing_extensions import Annotated
from frictionless import Package
from dpm.install import extract_source_packages
from pathlib import Path

app = typer.Typer()

@app.callback()
def callback():
    """
    Data package manager to install, update and remove data dependencies.
    """

@app.command()
def install(descriptor: Annotated[Path, typer.Argument()] = Path('data.yaml'), 
            output_dir: Annotated[Path, typer.Option()] = Path('datapackages')):
    """
    Download data packages (descriptor and resources data files) listed in package.sources and saves into datapackages/
    """

    with open("data.toml", "rb") as f:
        data_toml = tomllib.load(f)

    extract_source_packages(data_toml, output_dir)
