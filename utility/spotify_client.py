import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyClient():
    """
    Custom class to format Spotify Python libary (spotipy)
    from JSON into dataframes.
    """
    def __init__(
        self,
        client_id,
        client_secret,
        redirect_uri
    ):
        # Spotify processing
        # Set up authentication with refresh token support
        self.spotify_obj = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope='playlist-read-private playlist-read-collaborative',
                open_browser=False,  # Important for server environments
                cache_path='.spotifycache'  # Where refresh token is stored
            )
        )

    @staticmethod
    def pretty_print_dict(
        df
    ):
        print('-------------------')
        for key in df.keys():
            print(
                f"{key}\n"
                f"{df.get(key)}\n"
                "-------------------"
            )
        return

    def get_playlist_tracks(
        self,
        playlist_id: str
    ):
        """
        Get playlist tracks when given a playlist id
        """
        results_dict = self.spotify_obj.playlist_items(playlist_id)
        tracks = results_dict.get('items')

        # If there are more tracks than the limit
        # (usually 100), get the rest
        while results_dict.get('next'):
            results_dict = self.spotify_obj.next(results_dict)
            tracks.extend(results_dict.get('items'))

        return tracks

    def get_playlist_dict(
        self,
        playlist_id
    ):
        playlist_dict = self.spotify_obj.playlist(
            playlist_id=playlist_id
        )
        return playlist_dict
