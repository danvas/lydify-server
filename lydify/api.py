import time
from flask import Flask

from .config import init_config
from .logger import get_logger

app = Flask(__name__)

init_config(app)

LOGGER = get_logger(app.name, app.debug)


@app.route('/time')
def get_current_time():

    return {'time': time.time()}
