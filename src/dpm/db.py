import os
import logging
import sqlalchemy as sa

logger = logging.getLogger(__name__)

conn_string = os.getenv('SQLALCHEMY_URL') # or maybe DB_CONNECTION_STRING?
if conn_string:
    engine = sa.create_engine(conn_string)
else:
    logger.info('SQLALCHEMY_URL environment variable not found. dpm load will not work.')
    engine = None
