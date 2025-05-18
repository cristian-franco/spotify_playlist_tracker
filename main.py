import os
from dotenv import load_dotenv
import utility.discord_webhook as dw
import utility.spotify_client as sc
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from typing import List


def main():
    load_dotenv()

    discord_general_webhook_url = os.getenv('discord_general_webhook_url')
    target_playlist_id = os.getenv('target_playlist_id')
    client_id = os.getenv('spotify_app_client_id')
    client_secret = os.getenv('spotify_app_client_secret')
    redirect_uri = os.getenv('redirect_uri')

    # Spotify processing
    # Set up authentication with refresh token support
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope='playlist-read-private playlist-read-collaborative',
        open_browser=False,  # Important for server environments
        cache_path='.spotifycache'  # Where refresh token is stored
    ))

    # access specific playlist
    target_playlist_dict = sp.playlist(
    playlist_id=target_playlist_id
    )
    # sc.pretty_print_dict(target_playlist_dict)

    playlist_name = target_playlist_dict.get('name')

    tracks_list = sc.get_playlist_tracks(
        sp,
        target_playlist_id
    )

    current_timestamp = pd.Timestamp.now()

    playlist_df = sc.create_playlist_df(
        playlist_id=target_playlist_id,
        playlist_name=playlist_name,
        tracks_list=tracks_list,
        current_timestamp=current_timestamp
    )

    print(playlist_df)

    # Pull records for playlist from database

    # Compare new playlist_df to the database playlist_df

    # For new records, we will post a message detailing when they were
    # added, what songs there are, who added it (TO DO), and if any songs were removed
    # new_tracks_df
    #
    #
    # For records that are no longer in the playlist (were removed),
    # update the record for last_appearance

    target_playlist_len = len(playlist_df)

    message = f'''
    The {playlist_name} playlist currently has {target_playlist_len} songs.
    '''

    print(message)

    # # Send the message
    # dw.send_discord_message(
    #     discord_general_webhook_url,
    #     message
    # )

if __name__ == '__main__':
    main()
