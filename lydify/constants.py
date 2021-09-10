from enum import Enum

LYDIFY_MODE_ENV = "LYDIFY_MODE"
"""Environment variable name for configuration"""


class ConfigType(Enum):
    SPOTIFY = 0
    YOUTUBE = 1
