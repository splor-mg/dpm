from pprint import pprint
from frictionless import Package
from frictionless.formats.sql import SqlMapper
from sqlalchemy import create_engine, MetaData
from extract import save_source

def create_source(url):

    engine = create_engine('sqlite:///sqlite.db', echo=True)

    package = Package(url)

    metadata = MetaData()

    mapper = SqlMapper('sqlite')  # or 'postgresql'

    for resource in package.resources:
        schema = resource.schema
        table = mapper.write_schema(schema, table_name=resource.name)
        table.to_metadata(metadata)

    metadata.create_all(engine)

def load_sources(datapackage_master):

    print('datapackage_master.name:', datapackage_master.name)
    print('datapackage_master.resource_names', datapackage_master.resource_names)
    print('datapackage_master.sources', [datapackage_master.sources[i]['name'] for i in range(len(datapackage_master.sources))])

    for source in datapackage_master.sources:
        save_source(source)

# TODO Create main
# TODO use logging
# TODO transform in a python package

dp_spreadmart = Package('datapackage.json')
load_sources(dp_spreadmart)


