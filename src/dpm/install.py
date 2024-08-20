import re

import requests
import shutil
import logging
import os
from frictionless import Package, system
from pathlib import Path
from urllib.parse import urlparse

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

    # If it is a github url, proceed to get the commit hash
    if urlparse(source['path']).netloc in {'github.com', 'raw.githubusercontent.com'}:
        package.custom.update({'remote': get_commit_info(source)})
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


def get_commit_info(source):

    # Extract repository details from the URL
    parsed_url = parse_rawgithub_url(source["path"])

    # Set up headers for authentication
    varenv_name = source.get('token', None)
    if varenv_name:

        token = os.getenv(varenv_name)

        headers = {
            "Authorization": f"token {token}"
        }
    else:
        headers = {}

    # GitHub API URL to get the commit hash
    github_endpoint = "commits" if is_commit_sha(parsed_url['ref']) else "branches"

    api_url = f"https://api.github.com/repos/{parsed_url['user']}/{parsed_url['repo']}/{github_endpoint}/{parsed_url['ref']}"
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()  # Check for request errors

    return {
        "host": parsed_url['host'],
        "user": parsed_url['user'],
        "repo": parsed_url['repo'],
        "ref": parsed_url['ref'],
        "sha": response.json()['sha'] if github_endpoint == 'commits' else response.json()['commit']['sha']

    }


def parse_rawgithub_url(url):
    """
    Returns the parts of a github url in a dict
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')

    return dict(
        host=parsed_url.netloc,
        user=path_parts[0],
        repo=path_parts[1],
        ref=path_parts[2],
    )


def is_commit_sha(ref):
    """
    Returns True if ref is a valid commit SHA
    """
    if re.match(r"([a-z0-9]{40})", ref):
        return True
    else:
        return False
