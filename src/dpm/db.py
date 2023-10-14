import os
import sqlalchemy as sa

conn_string = os.getenv('SQLALCHEMY_URL') # or maybe DB_CONNECTION_STRING?
if conn_string:
    engine = sa.create_engine(conn_string)
