import requests
import shutil
import logging
import os
from frictionless import Package, system
from pathlib import Path

logger = logging.getLogger(__name__)

def update_session_headers(session, source):

    token = source.get('token')

    if token:
        session.headers['Authorization'] = f"Bearer {token}"
        return session
    else:
        return session


def extract_source_packages(package):
    for source in package.sources:
        logger.info(f'Downloading source package {source["name"]}...')
        extract_source_package(source)

def extract_source_package(source):


    session = requests.Session()
    # create a session and get the token if needed to auth a private repo
    session = update_session_headers(session, source)

    with system.use_context(http_session=session):
        package = Package(source['path'] )

    package_descriptor_path = Path('datapackages', source['name'], 'datapackage.json')
    package.dereference()
    package.to_json(package_descriptor_path)


    for resource in package.resources:
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

        logger.info(f'Data file of resource {resource.name} saved in {resource_path}')

