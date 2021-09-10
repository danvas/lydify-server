# Third party
from dotenv import load_dotenv
from os import getenv
from pathlib import Path

from .constants import LYDIFY_MODE_ENV

_ROOT_DIR = Path(__file__).parent
_mode = getenv(LYDIFY_MODE_ENV)

if _mode == "development":
    _env_file = _ROOT_DIR / ".env.development"
if _mode == "production":
    _env_file = _ROOT_DIR / ".env.production"
else:
    _env_file = _ROOT_DIR / ".env"

load_dotenv(_env_file)
