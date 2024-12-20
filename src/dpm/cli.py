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


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    """
    Data package manager to install, update and remove data dependencies.
    """
    
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

@app.command("install")
def cli_install(
    descriptor: Annotated[Path, typer.Argument()] = Path("data.toml"),
    output_dir: Annotated[Path, typer.Option()] = Path("datapackages"),
    package: Annotated[Optional[list[str]], typer.Option()] = None,
):
    """
    Download and install data packages listed in a descriptor file.

    This command-line interface (CLI) function reads a TOML descriptor file that
    specifies data packages and their associated resources. It downloads the
    specified packages and saves them into a designated output directory.
    This functionality is particularly useful for managing datasets and ensuring
    that the necessary resources are readily available for use.

    Args:
        descriptor (Path):
            The path to the TOML file containing the package descriptors. The
            default value is "data.toml". This file should define the sources
            from which the data packages will be downloaded.

        output_dir (Path, optional):
            The directory where the downloaded data packages and resources will
            be saved. The default is "datapackages". This directory will be created
            if it does not exist.

    Example:
        To install data packages from a specified TOML descriptor file:

        ```bash
        dpm install data.toml --output-dir datapackages
        ```

        This command will read the `data.toml` file, download the listed data
        packages, and save them into the `datapackages` folder.
    """

    with open(descriptor, "rb") as f:
        data_toml = tomllib.load(f)

    # filter data_toml based in the packages option list
    if package:
        data_toml = {"packages": {name: pkg for name, pkg in data_toml["packages"].items() if name in package}}
        available_packages = set(data_toml["packages"].keys())
        selected_packages = set(package)
        missing_packages = list(selected_packages - available_packages)

        if missing_packages:
            print(f"'{', '.join(missing_packages)}' did not match any packages in your data.toml. Interrupting.")
            return 1
    extract_source_packages(data_toml, output_dir)


@app.command("load")
def cli_load(
    manifest: Annotated[Path, typer.Argument()] = Path("data.toml"),
    package: Annotated[Path, typer.Option()] = None,
):
    """Load data packages into the database.

    This command-line interface (CLI) function loads data packages defined in
    a TOML manifest file into a specified database. It ensures that any necessary
    control tables are created, checks for existing resources to determine if they
    need to be updated, and handles the loading of resources based on their checksums.
    If a specific package is provided, it will load only that package; otherwise, it
    will load all packages defined in the manifest.

    Args:
        manifest (Path):
            The path to the TOML file that contains the data package descriptors.
            The default value is "data.toml". This file should list all the
            packages to be loaded into the database.

        package (Path, optional):
            The path to a specific data package (datapackage.json) to load.
            If provided, only this package will be loaded; otherwise, all packages
            from the manifest will be processed.

    Example:
        To load data packages defined in a manifest file:

        ```bash
        dpm load data.toml
        ```

        To load a specific data package:

        ```bash
        dpm load data.toml --package datapackages/package_name/datapackage.json
        ```

        This command will read the `data.toml` file and load the specified
        data package into the database, ensuring that control tables are
        managed appropriately.
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
    """
    Concatenate resources from multiple data packages into a single CSV file.

    This command-line interface (CLI) function allows the user to specify a pattern
    to match multiple data package files, or to provide a list of specific packages.
    The function concatenates resources from these packages based on the provided
    resource name(s) and optionally enriches the resulting DataFrame with additional
    identifier columns.

    Args:
        pattern (Optional[str]):
            A glob pattern to match data package filenames in the current directory.
            If provided, packages matching this pattern will be included in the
            concatenation process.

        package (list[str]):
            A list of specific data package filenames to include in the concatenation.
            If both `pattern` and `package` are provided, `package` will be included in
            the result alongside those matched by `pattern`.

        resource_name (list[str]):
            A list of resource names to concatenate from the specified packages. If not
            provided, the function will attempt to find common resource names across all
            packages. If there are no common resource names, a message will be printed
            and the function will exit.

        enrich (list[str], optional):
            A list of key-value pairs for enriching the DataFrame. Each pair should be in
            the format "key=value", where `key` is the name of the new column to create,
            and `value` is the property from the data package to use for populating that
            column. This option is used to add additional identifier columns to the
            concatenated output.

        output_dir (Path, optional):
            The directory where the output CSV files will be saved. Defaults to 'data'.
            This directory will be created if it does not already exist.

    Example:
        To concatenate resources with the same name from all packages matching a pattern:

        ```bash
        python script.py concat "*.json" --enrich "year=year"
        ```

        This command will match all JSON files in the current directory, concatenate the
        common resources, and add a new column `year` populated from the data package
        property `year`.

    """
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
    # frictionless.describe(source=output_dir / f"{resource_name}.csv", type=package, stats=True)


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
    logfile_path: Annotated[Path, typer.Argument()] = Path("logs/logfile.jsonl"),
    filter_type: Annotated[str, typer.Option(help="Filters json objects in the log file where the `Type` key has the value `--filter-type`.")] = None,
    output_dir: Annotated[Path, typer.Option(help="Folder where the report file will be saved.")] = Path.cwd(),
    format: Annotated[str, typer.Option()] = ".xlsx",
):
    """
    Export a json lines logfile to an specific file format.
    """
    supported_input_types = ['jsonl', 'json']
    supported_output_types = ['.xlsx', ]

    if is_complete_path(output_dir):
        print(f"ERROR: Cannot create the report, invalid output_dir.")
        typer.Exit(code=0)
        exit(code=0)

    if logfile_path.suffix in [".jsonl", ".json"]:
        print(f"Reading logfile_path: {logfile_path}...")

        df = read_jsonlines(logfile_path)

        if filter_type:
            df = filter_jsonlines(df, "type", filter_type)

        if format == '.xlsx':
            jsonlog_toexcel(df, output_dir, format)
            print(f"Report saved in {output_dir.absolute()/ f'report{format}'}.")
        else:
            print(f"ERROR: Cannot export to {format}. The supported formats are: {','.join(supported_output_types)}.")

    else:
        print(f"ERROR: Cannot create a report with {logfile_path.suffix} files. The supported input formats are: {','.join(supported_input_types)}.")
