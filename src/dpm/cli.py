import typer
from typing_extensions import Annotated
from frictionless import Package
from pathlib import Path
import logging
from typing import Optional
from typing_extensions import Annotated
import importlib.metadata
import os
from .utils import read_datapackage
from .concat import concat
from .normalize import normalize_package, normalize_resource

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from dpm.install import extract_source_packages

try:
    from dpm.load import read_manifest, load_package, create_if_not_exists_control_table
except ModuleNotFoundError:
    pass

logger = logging.getLogger(__name__)

app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(f"dpm, version {importlib.metadata.version('dpm')}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    """
    Data package manager to install, update and remove data dependencies.
    """


@app.command("install")
def cli_install(
    descriptor: Annotated[Path, typer.Argument()] = Path("data.toml"),
    output_dir: Annotated[Path, typer.Option()] = Path("datapackages"),
):
    """
    Download data packages (descriptor and resources data files) listed in package.sources and saves into datapackages/
    """
    with open(descriptor, "rb") as f:
        data_toml = tomllib.load(f)

    extract_source_packages(data_toml, output_dir)


@app.command("load")
def cli_load(
    manifest: Annotated[Path, typer.Argument()] = Path("data.toml"),
    package: Annotated[Path, typer.Option()] = None,
):
    """
    Load data packages into database
    """
    create_if_not_exists_control_table()

    if package:
        dp = Package(package)
        if not dp.name:
            logger.error(
                f"Package '{package}' is missing name. Aborting database load."
            )
        else:
            load_package(dp.name, dp)
    else:
        manifest = read_manifest("data.toml")
        for pkg_id in manifest["packages"].keys():
            path = Path("datapackages") / pkg_id / "datapackage.json"
            package = Package(path)
            load_package(pkg_id, package)


def _validate_enrich_option(option):
    if any(["=" not in value for value in option]):
        raise typer.BadParameter("required format is key=value")
    return option


@app.command("concat")
def cli_concat(
    pattern: Annotated[Optional[str], typer.Argument()] = None,
    package: Annotated[list[str], typer.Option()] = None,
    resource_name: Annotated[list[str], typer.Option()] = None,
    enrich: Annotated[
        list[str],
        typer.Option(
            "--enrich",
            "-e",
            help="Create a new column named 'name' with value from the data package property 'key'",
            callback=_validate_enrich_option,
        ),
    ] = None,
    output_dir: Annotated[Path, typer.Option()] = Path("data"),
):
    packages = []
    if pattern:
        packages = sorted(Path(".").glob(pattern))
    packages.extend(package)
    packages = [read_datapackage(package) for package in packages]
    if resource_name:
        resource_names = resource_name
    else:
        resource_names = set.intersection(
            *[set(package._package.resource_names) for package in packages]
        )
        if not resource_names:
            print(
                "There are no resources with the same name in all packages to concatenate..."
            )
            typer.Exit(code=0)
    id_cols = dict(pair.split("=") for pair in enrich)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Concatenating resources: {', '.join(resource_names)}")
    for resource_name in resource_names:
        df = concat(*packages, resource_name=resource_name, id_cols=id_cols)
        df.to_csv(output_dir / f"{resource_name}.csv", index=False, encoding="utf-8")


@app.command("normalize")
def cli_normalize(
    source: Annotated[str, typer.Argument()],
    output_dir: Annotated[Path, typer.Option()] = ".",
    data_dir: Annotated[Path, typer.Option()] = "data",
    resource_name: Annotated[str, typer.Option()] = None,
    metadata: Annotated[bool, typer.Option("--metadata")] = False,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    package = Package(source)
    
    if resource_name:
        resource = package.get_resource(resource_name)
        normalize_resource(resource, data_dir)
        raise typer.Exit()

    if metadata:
        normalize_package(package, output_dir, data_dir)    
        raise typer.Exit()

    for resource in package.resources:
        normalize_resource(resource, data_dir)
    normalize_package(package, output_dir, data_dir)
