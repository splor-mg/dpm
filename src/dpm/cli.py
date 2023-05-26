import typer
from frictionless import Package
from dpm.install import extract_sources

app = typer.Typer()

@app.callback()
def callback():
    """
    Data package manager to install, update and remove data dependencies.
    """

@app.command()
def install(descriptor: str = 'datapackage.yaml'):
    """
    Download data packages (descriptor and resources data files) listed in package.sources and saves into datapackages/
    """
    package = Package(descriptor)
    extract_sources(package)
