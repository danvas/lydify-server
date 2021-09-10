import base64
import os
import random
import string

from .constants import ConfigType


def create_state_key(size: int = 15) -> str:
    """
        Creates a state key for the authorization request. State keys are used to make sure that
        a response comes from the same place where the initial request was sent. This prevents attacks,
        such as forgery.
    ``

        Returns:
            str: A state key with a parameter specified size.
    """
    # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
    return "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))


def base64_encode(astring: str):
    return base64.urlsafe_b64encode(astring.encode()).decode()


def get_authorization(config_type: ConfigType):

    if config_type.name == "SPOTIFY":
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        b64_str = base64_encode(f"{client_id}:{client_secret}")

        return f"Basic {b64_str}"

    if config_type.name == "YOUTUBE":
        raise NotImplemented("YoutubeConfig incomplete")
