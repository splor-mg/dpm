import sqlalchemy as sa
from frictionless import Package, formats, Resource
import frictionless
import logging
from datetime import datetime
from .db import engine
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

logger = logging.getLogger(__name__)

def read_manifest(path):
    with open(path, "rb") as f:
        result = tomllib.load(f)
    return result

def create_database_table(package_id, resource):
    metadata = sa.MetaData(schema=package_id)
    mapper = formats.sql.SqlMapper(engine.url.drivername)
    table = mapper.write_schema(resource.schema, table_name = resource.name)
    table.to_metadata(metadata)

    bigint_fields = [
        field.name 
        for field in resource.schema.fields 
        if isinstance(field, frictionless.fields.IntegerField) and field.custom.get('bigint')
    ]
    
    for field in bigint_fields:
        sa.Table(resource.name, metadata, sa.Column(field, sa.BigInteger), extend_existing=True)
    metadata.create_all(engine, tables=[metadata.tables[f'{package_id}.{resource.name}']])

def create_database_schema(schema):
    with engine.connect() as conn:
        stm = sa.schema.CreateSchema(schema, if_not_exists=True)
        conn.execute(stm)
        conn.commit()

def load_resource(package_id, resource):
    table_name = f'{package_id}.{resource.name}'
    logger.info(f'Loading {table_name}')
    metadata = sa.MetaData(schema=package_id)
    metadata.reflect(bind=engine)
    table = metadata.tables[table_name]
    data = resource.read_rows()
    with engine.connect() as conn:
        conn.execute(sa.insert(table), data)
        conn.execute(
                     sa.text("""
                             INSERT INTO control_table 
                             VALUES (:package_name, :resource_name, :checksum)
                             ON CONFLICT (package_name, resource_name) DO UPDATE
                             SET checksum = excluded.checksum
                             """),
                     {'package_name': package_id, 'resource_name': resource.name, 'checksum': resource.hash}
                    )
        conn.commit()

def resource_need_update(package_id:str, resource: Resource):
    result = True
    with engine.connect() as conn:
        resultset = conn.execute(sa.text("""
                            SELECT checksum
                            FROM control_table
                            WHERE package_name = :package_name and resource_name = :resource_name
                                """),
                        {'package_name': package_id, 'resource_name': resource.name}
                        ).fetchall()
    if resultset and resultset[0][0] == resource.hash:
        result = False
    return result

def drop_table(package_id:str, resource: Resource):
    if sa.inspect(engine).has_table(resource.name, schema=package_id):
        with engine.connect() as conn:
            conn.execute(sa.text(f'DROP TABLE {package_id}.{resource.name}'))
            conn.commit()
    return True

def load_package(package_id:str, package: Package):
    create_database_schema(package_id)
    for resource in package.resources:
        if resource_need_update(package_id, resource):
            drop_table(package_id, resource)
            create_database_table(package_id, resource)
            load_resource(package_id, resource)

def create_if_not_exists_control_table():    
    if not sa.inspect(engine).has_table('control_table'):
        metadata = sa.MetaData()
        metadata.reflect(bind=engine)

        table = sa.Table(
            'control_table',
            metadata,
            sa.Column('package_name', sa.String, primary_key=True),
            sa.Column('resource_name', sa.String, primary_key=True),
            sa.Column('checksum', sa.String),
        )

        metadata.create_all(engine, tables=[table])
