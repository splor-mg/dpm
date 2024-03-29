import requests
import shutil
import logging
import os
from frictionless import Package, system
from pathlib import Path

logger = logging.getLogger(__name__)

def update_session_headers(session, source):

    varenv_name = source.get('token', None)
    if varenv_name:
        logger.info(f'Using token stored in {varenv_name} for accessing data package {source["name"]}')
        token = os.getenv(varenv_name)
        session.headers['Authorization'] = f"Bearer {token}"

    return session

def extract_source_packages(toml_package, output_dir):
    for key, source in toml_package["packages"].items():
        source["name"] = key
        logger.info(f'Downloading package {source["name"]}....')
        extract_source_package(source, output_dir)

def extract_source_package(source, output_dir):


    session = requests.Session()
    # create a session and get the token if needed to auth a private repo
    session = update_session_headers(session, source)

    with system.use_context(http_session=session):
        package = Package(source["path"])

    package_descriptor_path = Path(output_dir, source["name"], 'datapackage.json')
    package.dereference()


    fetch_resources = source.get('resources', package.resource_names)

    for res in [res for res in package.resource_names if res not in fetch_resources]:
        package.remove_resource(res)



    package.to_json(package_descriptor_path)

    if package.resources == []:
        logger.warning(f'All resources were not found for package "{source["name"]}". '
                       f'Please check your data.toml file.')
        return

    for resource_name in fetch_resources:
        if resource_name in package.resource_names:

            resource = package.get_resource(resource_name)

            resource_remotepath = f'{resource.basepath}/{resource.path}'

            response = session.get(str(resource_remotepath), stream=True)
            response.raise_for_status()

            resource_path = Path(package_descriptor_path.parent, resource.path)
            resource_path.parent.mkdir(parents=True, exist_ok=True)

            if 'text' in resource.mediatype:
                response.raw.decode_content = True
            else:
                response.raw.decode_content = False

            with open(resource_path, 'wb') as file:
                shutil.copyfileobj(response.raw, file)

            logger.info(f'Data file of resource "{resource.name}" saved in "{resource_path}"')

        else:
            logger.warning(f'Resource "{resource_name}" not found for package "{package.name}". '
                        f'Please check your `data.toml` file.')

