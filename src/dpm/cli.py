import sys
import typer
import logging
import importlib.metadata

from frictionless import Package, describe
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated
from .utils import read_datapackage, read_jsonlines, filter_jsonlines, jsonlog_toexcel, is_complete_path
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

app = typer.Typer(pretty_exceptions_show_locals=False)


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
    package: Annotated[Optional[list[str]], typer.Option()] = None,
):
    """
    Download data packages (descriptor and resources data files) listed in package.sources and saves into datapackages/
    """
    with open(descriptor, "rb") as f:
        data_toml = tomllib.load(f)

    # filter data_toml based in the packages option list
    if package:
        data_toml = {"packages": {name: pkg for name, pkg in data_toml["packages"].items() if name in package}}

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
    metadata_dir: Annotated[Path, typer.Option()] = Path("."),
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
        print(output_dir / f"{resource_name}.csv")
    #frictionless.describe(source=output_dir / f"{resource_name}.csv", type=package, stats=True)


@app.command("normalize")
def cli_normalize(
    source: Annotated[str, typer.Argument()],
    data_dir: Annotated[Path, typer.Option()] = "data",
    resource_name: Annotated[str, typer.Option()] = None,
    json_ext: Annotated[bool, typer.Option("--json")] = False,
    yaml_ext: Annotated[bool, typer.Option("--yaml")] = False,
    metadata_dir: Annotated[Path, typer.Option()] = "."
):

    data_dir.mkdir(parents=True, exist_ok=True)
    package = Package(source)

    if resource_name:
        resource = package.get_resource(resource_name)
        resource = normalize_resource(resource, data_dir, metadata_dir)

        with open(metadata_dir, 'w', encoding='utf-8') as f:

            if yaml_ext:
                f.write(resource.to_yaml())

            else:
                f.write(resource.to_json())

        #sys.stdout.write(resource.to_yaml() if yaml_ext else resource.to_json())


        raise typer.Exit()

    for resource in package.resources:
        normalize_resource(resource, data_dir, metadata_dir)
    package = normalize_package(package, data_dir, metadata_dir)

    with open(Path(metadata_dir, "datapackage.json"), 'w', encoding='utf-8') as f:

        if yaml_ext:
            f.write(package.to_yaml())

        else:
            f.write(package.to_json())





@app.command("report")
def cli_report(
    logfile_path: Annotated[Path, typer.Argument()] = Path("logs/logfile.json"),
    test_name: Annotated[str, typer.Option()] = None,
    output_dir: Annotated[Path, typer.Option()] = Path.cwd() / "report.xlsx",
    format: Annotated[str, typer.Option()] = ".xlsx",
):
    supported_input_types = ['jsonl', ]
    supported_output_types = ['.xlsx', ]

    if not is_complete_path(output_dir):
        print(f"Cannot create the report, invalid output_dir.")
        typer.Exit(code=0)
        exit(0)

    if logfile_path.suffix == ".jsonl":
        print(f"Reading logfile_path {logfile_path}...")
        df = read_jsonlines(logfile_path)

        if test_name:
            df = filter_jsonlines(df, "type", test_name)

        if format == '.xlsx':

            jsonlog_toexcel(df, output_dir)
            print(f"Report saved in {output_dir.absolute()}.")
        else:
            print(f"Cannot export to {format}. The supported formats are: {','.join(supported_output_types)}.")

    else:
        print(f"Cannot create a report with {logfile_path.suffix} files. The supported input formats are: {','.join(supported_input_types)}.")
