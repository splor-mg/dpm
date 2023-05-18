import requests
import shutil
import os
import mimetypes
from urllib.parse import urlparse
from frictionless import Package, Resource
from transform import merge_remove_path_redundancies
from pathlib import Path

# TODO replace os package for pathlib

def save_source(source):

    dataset_dir = 'datapackages'
    file_dir = os.path.join(dataset_dir, source['name'])

    os.makedirs(file_dir, exist_ok=True)

    file_path = os.path.join(file_dir, 'datapackage.json')

    dp_source = Package(source['path'])
    dp_source.to_json(file_path) # Done!

    # TODO : 1. para cada resource de cada source, salvar os arquivos de dados na pasta do datapackage obedecendo a estrutura relativa

    for resource in dp_source.resources:

        resource_remotepath = f'{resource.basepath}/{resource.path}'
        response = requests.get(str(resource_remotepath), stream=True)
        response.raise_for_status()

        #datapackage_path = parsed_url.path.lstrip('/') # TODO change name, not always a dp

        #url_dir = os.path.join(source['name'], os.path.dirname(datapackage_path))

        #dataset_dir = 'datapackages' # TODO not put string literals inside a function. Parameter, constant or arg?
        # os.makedirs(resource_path.parent, exist_ok=True)

        resource_path = Path(file_dir, resource.path)
        resource_path.parent.mkdir(parents=True, exist_ok=True)


        #file_path = merge_remove_path_redundancies(file_dir, datapackage_path)
        #file_path = os.path.join(file_dir, datapackage_path) # if above works, remove this


        #if mimetypes.guess_type(file_path)[0] in ('text/plain', 'text/csv'):
        if 'text' in resource.mediatype:
            response.raw.decode_content = True
        else:
            response.raw.decode_content = False

        with open(resource_path, 'wb') as file:
            shutil.copyfileobj(response.raw, file)

    # TODO : 2. tratar depois os casos que o path do resouce de uma source é uma URL.
    # TODO : 3. tratar situação de quando a source do datapackge_master for um arquivo local (frictionless.byte_stream() deve tratar os dois casos melhor.
    # TODO : 4. Como tratar um data_resource que não tem schema?

