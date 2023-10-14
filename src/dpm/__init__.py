import logging
from pathlib import Path
from dotenv import load_dotenv

LOG_FORMAT = '%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, level=logging.INFO)

load_dotenv(dotenv_path=Path('.', '.env'))
