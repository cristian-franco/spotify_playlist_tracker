import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from typing import List

def pretty_print_dict(d):
    print('-------------------')
    for key in d.keys():
        print(key)
        print(d.get(key))
        print('-------------------')

    return


def get_playlist_tracks(
    sp,
    playlist_id: str
):
    '''
    Get playlist tracks when given a playlist id
    '''
    results_dict = sp.playlist_items(playlist_id)
    tracks = results_dict.get('items')

    # If there are more tracks than the limit
    # (usually 100), get the rest
    while results_dict.get('next'):
        results_dict = sp.next(results_dict)
        tracks.extend(results_dict.get('items'))

    return tracks


def create_playlist_df(
    playlist_id: str,
    playlist_name: str,
    tracks_list: List,
    current_timestamp: pd.Timestamp
) -> pd.DataFrame:
    '''
    Constructs a DataFrame, one row/record per song,
    each with the playlist name, playlist id,
    song id, and song name attached to it
    as well as a timestamp of when it was generated
    '''
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
