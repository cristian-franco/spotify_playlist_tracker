from typing import List
import pandas as pd


class SpotifyFormatter():
    def __init__(self):
        pass

    @staticmethod
    def create_playlist_df(
        playlist_id: str,
        playlist_name: str,
        tracks_list: List,
        current_timestamp: pd.Timestamp
    ) -> pd.DataFrame:
        """
        Constructs a DataFrame, one row/record per song,
        each with the playlist name, playlist id,
        song id, and song name attached to it
        as well as a timestamp of when it was generated
        """
        combined_df = pd.DataFrame()
        for track in tracks_list:
            # Check if it's a track (playlists can contain other things)
            if track['track']:
                track_name = track['track']['name']
                artist_name = track['track']['artists'][0]['name']
                # print(f"{artist_name} - {track_name}")

                data = {
                    'playlist_id': [playlist_id],
                    'playlist_name': [playlist_name],
                    'track_name': [track_name],
                    'artist_name': [artist_name],
                    'generation_ts': [current_timestamp]
                }

                new_row_df = pd.DataFrame(data)

                # Concatenate the new DataFrame with the original DataFrame
                combined_df = pd.concat(
                    [combined_df, new_row_df],
                    ignore_index=True
                )
        return combined_df


