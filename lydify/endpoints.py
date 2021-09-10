import time

from .spotify import fetch_playlists, fetch_playlist, login, auth_callback, handle_404

from flask import Flask


def register(app: Flask):
    spotify_config = app.config["SPOTIFY"]

    @app.route("/time")
    def get_current_time():
        return {"time": time.time()}

    @app.route("/authorize")
    def authorize():
        return login(spotify_config)

    @app.route("/callback")
    def callback():
        return auth_callback(spotify_config)

    @app.errorhandler(404)
    def error_404(e):
        return handle_404(e)

    @app.route("/playlists", methods=["GET"])
    def playlists():
        return fetch_playlists(spotify_config)

    @app.route("/playlist/<playlist_id>", methods=["GET"])
    def playlist(playlist_id):
        return fetch_playlist(playlist_id, spotify_config)
