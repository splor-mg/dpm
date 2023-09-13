import typer
from typing_extensions import Annotated
from frictionless import Package
from dpm.install import extract_source_packages
from pathlib import Path
from dpm.diff import diff_schema

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
    package = Package(descriptor)
    extract_source_packages(package, output_dir)

@app.command()
def diff(source: str, target: str, resource_name: str):
    source_package = Package(source)
    target_package = Package(target)
    diff_schema(source_package, target_package, resource_name)
    