from .config import init_config
from .endpoints import register as register_endpoints
from .logger import get_logger

from flask import Flask

app = Flask(__name__)

init_config(app)

LOGGER = get_logger(app.name, app.debug)

try:
    register_endpoints(app)
except Exception as ex:
    print(ex)
    LOGGER.critical(str(ex))
