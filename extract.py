import requests
import shutil
import os
from urllib.parse import urlparse
from frictionless import Package, Resource
from pathlib import Path
import logging

def extract_sources(datapackage_master):


    logging.info(f'Utilizando datapackage master: {datapackage_master.name}')

    for source in datapackage_master.sources:
        logging.info(f'Utlizando source "{source["name"]}".')
        extract_resources(source)


def extract_resources(source):

    dataset_dir = 'datapackages'
    file_dir = os.path.join(dataset_dir, source['name'])


    os.makedirs(file_dir, exist_ok=True)

    file_path = os.path.join(file_dir, 'datapackage.json')

    dp_source = Package(source['path'])
    dp_source.to_json(file_path) # Done!
    logging.info(f'datapackage.json salvo em {file_path} ')

    for resource in dp_source.resources:

        resource_remotepath = f'{resource.basepath}/{resource.path}'
        response = requests.get(str(resource_remotepath), stream=True)
        response.raise_for_status()

        resource_path = Path(file_dir, resource.path)
        resource_path.parent.mkdir(parents=True, exist_ok=True)

        if 'text' in resource.mediatype:
            response.raw.decode_content = True
        else:
            response.raw.decode_content = False

        with open(resource_path, 'wb') as file:
            shutil.copyfileobj(response.raw, file)

        #print(f'Fonte de dados (resource) "{resource.name}" salva em {resource_path}')
        logging.info(f'Fonte de dados (resource) "{resource.name}" salva em {resource_path}')
    # TODO : 2. tratar depois os casos que o path do resouce de uma source é uma URL.
    # TODO : 3. tratar situação de quando a source do datapackge_master for um arquivo local (frictionless.byte_stream() deve tratar os dois casos melhor.
    # TODO : 4. Como tratar um data_resource que não tem schema?

