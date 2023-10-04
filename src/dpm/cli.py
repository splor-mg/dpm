import typer
from typing_extensions import Annotated
from dpm.install import extract_source_packages
from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


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

    with open("data.toml", "rb") as f:
        data_toml = tomllib.load(f)

    extract_source_packages(data_toml, output_dir)
