import os
from dotenv import load_dotenv
import utility.discord_webhook as dw
import pandas as pd
import utility.spotify_client as sc
import utility.spotify_formatter as sf
import utility.postgres_db as pg_db


def main():
    current_timestamp = pd.Timestamp.now()

    load_dotenv()

    discord_general_webhook_url = os.getenv('discord_general_webhook_url')
    playlist_id = os.getenv('playlist_id')
    client_id = os.getenv('spotify_app_client_id')
    client_secret = os.getenv('spotify_app_client_secret')
    redirect_uri = os.getenv('redirect_uri')

    spotify_client = sc.SpotifyClient(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri
    )

    # access specific playlist
    playlist_dict = spotify_client.get_playlist_dict(
        playlist_id=playlist_id
    )

    # sc.pretty_print_dict(target_playlist_dict)

    playlist_name = playlist_dict.get('name')

    tracks_list = spotify_client.get_playlist_tracks(
        playlist_id=playlist_id
    )
    # print(tracks_list)

    # each tracks_list item contains a track_dict
    # in this dict, we should add a couple of extra fields
    # added_at: timestamp
    # added_by: dict containing id (name)
    #
    # track_id has to be here somewhere
    # TO DO - find track_id

    spotify_formatter = sf.SpotifyFormatter()

    playlist_df = spotify_formatter.create_playlist_df(
        playlist_id=playlist_id,
        playlist_name=playlist_name,
        tracks_list=tracks_list,
        current_timestamp=current_timestamp
    )
    print("playlist_df")
    print(playlist_df)

    # Pull records for playlist from database

    postgres_db = pg_db.PostgresDB()

    sql_query = """
    select * from playlist_tracks    
    """

    stored_tracks_df = postgres_db.execute_query(sql_query)

    postgres_db.close_connection()

    print("stored_tracks_df")
    print(stored_tracks_df)
    print(len(stored_tracks_df))

    # columns
    # Columns: [id, playlist_id, track_id, user_id, snapshot_id, created_at, updated_at]



    # Compare new playlist_df to the database playlist_df



    # For new records, we will post a message detailing when they were
    # added, what songs there are, who added it (TO DO), and if any songs were removed
    # new_tracks_df
    #
    #
    # For records that are no longer in the playlist (were removed),
    # update the record for last_appearance

    message = f'''
    The {playlist_name} playlist currently has {len(playlist_df)} songs.
    '''

    print(message)

    # Send the message
    # dw.send_discord_message(
    #     discord_general_webhook_url,
    #     message
    # )


if __name__ == '__main__':
    main()
