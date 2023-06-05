import requests
import shutil
from frictionless import Package
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def extract_source_packages(package):
    for source in package.sources:
        logger.info(f'Downloading source package {source["name"]}...')
        extract_source_package(source)

def extract_source_package(source):
    package = Package(source['path'])
    package_descriptor_path = Path('datapackages', source['name'], 'datapackage.json')
    package.dereference()
    package.to_json(package_descriptor_path)

    for resource in package.resources:
        resource_remotepath = f'{resource.basepath}/{resource.path}'
        headers = {'Authorization': f'token {github_token}'}
        response = requests.get(str(resource_remotepath), headers=headers, stream=True)
        #response = requests.get(str(resource_remotepath), stream=True)

        response.raise_for_status()

        resource_path = Path(package_descriptor_path.parent, resource.path)
        resource_path.parent.mkdir(parents=True, exist_ok=True)

        if 'text' in resource.mediatype:
            response.raw.decode_content = True
        else:
            response.raw.decode_content = False

        with open(resource_path, 'wb') as file:
            shutil.copyfileobj(response.raw, file)

        logger.info(f'Data file of resource {resource.name} saved in {resource_path}')
