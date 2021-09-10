# from .api import app
"""
AUTHENTICATION: To make a request to the Spotify API, the application needs an access
token for the user. This token expires every 60 minutes. To acquire a new token, the 
refresh token can be sent to the API, which will return a new access token.
"""

# Python
import time

# Third party
import curlify
from flask import session, redirect, make_response, request, jsonify
import requests


from .utils import create_state_key
from .config import SpotifyConfig

SCOPES = "playlist-read-private"  # user-read-private?
"""https://developer.spotify.com/documentation/general/guides/scopes/"""


def get_user_info(session, config: SpotifyConfig):
    """
    Gets user information such as username, user ID, and user location.
    Returns: Json response of user information
    """
    url = "https://api.spotify.com/v1/me"
    payload = make_get_request(session, url, config)

    if payload == None:
        return None

    return payload


def refresh_token(refresh_token, config: SpotifyConfig):
    """
    Requests an access token from the Spotify API with a refresh token. Only called if an access
    token and refresh token were previously acquired.
    Returns: either [access token, expiration time] or None if request failed
    """
    token_url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": config.authorization,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {"refresh_token": refresh_token, "grant_type": "refresh_token"}
    post_response = requests.post(token_url, headers=headers, data=body)

    # 200 code indicates access token was properly granted
    if post_response.status_code == 200:
        return post_response.json()["access_token"], post_response.json()["expires_in"]
    else:
        print("refresh_token:" + str(post_response.status_code))
        return None


def is_token_valid(session, config) -> bool:
    """
    Determines whether new access token has to be requested because time has expired on the
    old token. If the access token has expired, the token refresh function is called.
    Returns: False if error occured or True if access token is okay
    """
    if time.time() > session["token_expiration"]:
        payload = refresh_token(session["refresh_token"], config)

        if payload != None:
            session["token"] = payload[0]
            session["token_expiration"] = time.time() + payload[1]
        else:
            print("is_token_valid")
            return False

    return True


def get_token(code: str, config: SpotifyConfig):
    token_url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": config.authorization,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {
        "code": code,
        "redirect_uri": config.redirect_uri,
        "grant_type": "authorization_code",
    }

    post_response = requests.post(token_url, headers=headers, data=body)
    curled = curlify.to_curl(post_response.request, compressed=True)
    print(post_response.status_code, curled)
    # 200 code indicates access token was properly granted
    if post_response.status_code == 200:
        json = post_response.json()
        return json["access_token"], json["refresh_token"], json["expires_in"]
    else:
        print("get_token:" + str(post_response.status_code))
        return None


def make_get_request(session, url, config: SpotifyConfig, params={}):
    """
    Makes a GET request with the proper headers. If the request succeeds, the json parsed
    response is returned. If the request fails because the access token has expired, the
    check token function is called to update the access token.
    Returns: Parsed json response if request succeeds or None if request fails
    """
    token = session["token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, params=params)
    print(curlify.to_curl(response.request, compressed=True))
    # 200 code indicates request was successful
    if response.status_code == 200:
        return response.json()

    # if a 401 error occurs, update the access token
    elif response.status_code == 401 and is_token_valid(session, config):
        return make_get_request(session, url, config, params)
    else:
        print("make_get_request:" + str(response.status_code))
        return None


def login(config: SpotifyConfig) -> "Response":
    response_type = "code"
    state_key = create_state_key()
    session["state_key"] = state_key
    print("spotify config!!!!!", config)
    # redirect user to Spotify authorization page
    query_string = (
        "https://accounts.spotify.com/en/authorize?"
        f"response_type={response_type}&"
        f"client_id={config.client_id}&"
        f"redirect_uri={config.redirect_uri}&"
        f"scope={SCOPES}&"
        f"state={state_key}"
    )
    print(f"query_string = {query_string}")
    res = redirect(query_string)
    print(f"-----res", type(res), dir(res))
    response = make_response(res)
    print("Response!!!!!! ", type(response), dir(response))
    return response


def auth_callback(config: SpotifyConfig):
    print(f"+++++ request.args= {request.args}")
    print(f"+++++ session['state_key']= {session.get('state_key')}")

    # make sure the response came from Spotify
    if request.args.get("state") != session.get("state_key"):
        return redirect("/error")
    if request.args.get("error"):
        return redirect("/error")
    else:
        code = request.args.get("code")
        session.pop("state_key", None)

        # get access token to make requests on behalf of the user
        payload = get_token(code, config)
        if payload != None:
            session["token"] = payload[0]
            session["refresh_token"] = payload[1]
            session["token_expiration"] = time.time() + payload[2]
        else:
            return redirect("/error")

    current_user = get_user_info(session, config)
    session["user_id"] = current_user["id"]
    print("new user:" + session["user_id"])

    return redirect("/playlists")


def handle_404(e):
    if request.method == "GET":
        return redirect(f"/error")
    return e


def get_user_info(session, config: SpotifyConfig):
    """
    Gets user information such as username, user ID, and user location.
    Returns: Json response of user information
    """
    url = "https://api.spotify.com/v1/me"
    payload = make_get_request(session, url, config)

    if payload == None:
        return None

    return payload


def fetch_playlists(config: SpotifyConfig):
    """
    Create Feature: Page allows users to enter artists/tracks and creates a playlist based
    on these entries.
    """
    # make sure application is authorized for user
    if session.get("token") == None or session.get("token_expiration") == None:
        session["previous_url"] = "/get-playlists"
        return redirect("/authorize")

    # collect user information
    if session.get("user_id") == None:
        current_user = get_user_info(session)
        session["user_id"] = current_user["id"]
    url = "https://api.spotify.com/v1/me/playlists"
    payload = make_get_request(session, url, config, params={"limit": 50})
    playlists = payload.get("items", [])
    names = [{"name": pl["name"], "id": pl["id"]} for pl in playlists]
    print("********** get_playlists payload:", payload)
    if payload == None:
        return None
    return jsonify(names)


def fetch_playlist(playlist_id: str, config: SpotifyConfig):
    """Get the details of given playlist."""
    # make sure application is authorized for user
    if session.get("token") == None or session.get("token_expiration") == None:
        session["previous_url"] = "/playlists"
        return redirect("/authorize")

    # collect user information
    if session.get("user_id") == None:
        current_user = get_user_info(session)
        session["user_id"] = current_user["id"]
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    fields = "name,description,tracks"
    payload = make_get_request(session, url, config, params={"fields": fields})

    if payload == None:
        print("*** No playlists!")
        return None
    return jsonify(payload)
