import webbrowser
import subprocess
import pathlib
import shutil
import os
import csv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from concurrent.futures import ThreadPoolExecutor, as_completed

from requests.adapters import HTTPAdapter
from requests import Session
from urllib3.util.retry import Retry
from credentials import *

# Set up your credentials
# SPOTIPY_CLIENT_ID = "yours here"
# SPOTIPY_CLIENT_SECRET = "yours here"
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "playlist-modify-private playlist-read-private playlist-read-collaborative user-library-modify"

def format_cell_artist(cell) -> str:
    return cell

def format_cell_song(cell) -> str:
    return cell

def formatSpotifyPlaylist(playlist_file_name):
    playlist_name = playlist_file_name.replace('.csv', '')

    # ensures playlist name is formatted as snake case
    if " " in playlist_file_name:
        playlist_file_name = ''.join([char if char != " " else "_" for char in playlist_file_name])
    
    # checks if playlist exists
    if playlist_file_name in os.listdir('Spotify_Exported_PlayLists'):

        # Determine the file name for the formatted playlist
        formatted_file_path = f'Formatted_PlayLists/{playlist_file_name.replace(".csv", ".txt")}'

        # checks if formatted playlist already exists
        version = 1
        while os.path.exists(formatted_file_path):
            formatted_file_path = f'Formatted_PlayLists/{playlist_file_name.replace(".csv", "")}_{version}.txt'
            version += 1

        # open files for formatting
        with open(formatted_file_path, 'w') as formattedTXT:
            with open(f'Spotify_Exported_PlayLists/{playlist_file_name}', 'r') as unformattedCSV:
                csv_reader = csv.reader(unformattedCSV)
                for row in csv_reader:
                    for index, cell in enumerate(row):
                        if index == 1:
                            cell_to_write = format_cell_song(cell)
                            formattedTXT.write(f'{cell_to_write}\n')
                        elif index == 3:
                            cell_to_write = format_cell_artist(cell)
                            formattedTXT.write(f'{cell_to_write}\n')
                        else:
                            continue

        # move spotify playlist to Unformatted_PlayLists_Archive folder
        shutil.move(f'Spotify_Exported_PlayLists/{playlist_file_name}', f'Unformatted_PlayLists_Archive/{playlist_file_name}')
        return
    else:
        print(f'{playlist_file_name} not found')
        return

def formatApplePlaylist(playlist_file_name):
    playlist_name = playlist_file_name.replace('.txt', '')

    # ensures playlist name is formatted as snake case
    if " " in playlist_file_name:
        playlist_file_name = ''.join([char if char != " " else "_" for char in playlist_file_name])
    
    # checks if playlist exists
    if playlist_file_name in os.listdir('Apple_Exported_PlayLists'):
        possible_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\'\"();\\/@#$%!?<>.`~=+^&*_-"
        # copy playlist to Formatted_PlayLists folder
        with open(f'Apple_Exported_PlayLists/{playlist_file_name}', 'r',encoding='ISO-8859-1') as unformattedTXT:
            with open(f'Formatted_PlayLists/{playlist_file_name}', 'w') as formattedTXT:
                for line in unformattedTXT:
                    if "(Remastered)" in line:
                        line = line.replace("(Remastered)", "")
                    for char in line:
                        if char in possible_chars or char == ' ':
                            formattedTXT.write(char)
                        else:
                            break
                    formattedTXT.write('\n')
        
        shutil.move(f'Apple_Exported_PlayLists/{playlist_file_name}', f'Unformatted_PlayLists_Archive/{playlist_file_name}')
    else:
        print(f'{playlist_file_name} not found')
        return

def format_all_playlists():
    # format all Spotify playlists
    for playlist in os.listdir('Spotify_Exported_PlayLists'):
        if playlist.endswith('.csv'):
            formatSpotifyPlaylist(playlist)

    # format all Apple playlists
    for playlist in os.listdir('Apple_Exported_PlayLists'):
        if playlist.endswith('.txt'):
            formatApplePlaylist(playlist)

def importApplePlaylist():
    # prompt user for playlist name
    playlist_name = input('Enter the name of the playlist to import: ')
    print(f'importing {playlist_name}...')
    file_name = ''.join([char if char != " " else "_" for char in playlist_name])
    file_path = f'{str(pathlib.Path.home()).replace("/", ":")[1:]}:Desktop:Apple_Music_Spotify_Bijection:Apple_Exported_PlayLists:{file_name}.txt'

    # create the file path if it doesn't exist
    with open(f'Apple_Exported_PlayLists/{file_name}.txt', 'w'):
        pass

    # run apple script to import playlist
    try:
        subprocess.run(['osascript', 'exportApplePlaylist.scpt', playlist_name, file_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

    return

def importSpotifyPlaylist():
    print("manually import spotify playlist by using the website launched in your browser")
    
    # opens website in browser
    url = 'https://exportify.net'
    webbrowser.open(url)

    return

def createApplePlaylist():
    # format all playlists
    format_all_playlists()

    # prompt user for playlist name
    possible_playlists = os.listdir('Formatted_PlayLists')
    print('\npossible playlists:')
    for index, playlist in enumerate(possible_playlists):
        if playlist.endswith('.txt'):
            print(f' {index} = {playlist}')

    # prompt user for playlist to create
    playlist_index = int(input('Enter the number of the playlist to create: '))
    playlist_file_name = possible_playlists[playlist_index]
    playlist_name = f"NEW_{str(playlist_file_name).replace('.txt', '')}"

    print(f'creating {playlist_name} from file "{playlist_file_name}"...')

    # run apple script to create playlist
    try:
        # Get the absolute path to the formatted playlist file
        formatted_file_path = os.path.abspath(f'Formatted_PlayLists/{playlist_file_name}')

        # Convert the path to the format expected by AppleScript
        formatted_file_path = formatted_file_path.replace('/', ':')

        subprocess.run(['osascript', 'createApplePlaylist.scpt', playlist_name, formatted_file_path[1:]], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

    return

def add_song_to_spotify(sp, playlist_id, current_song, current_artist):
    # Search for the track on Spotify
    results = sp.search(q=f"track:{current_song} artist:{current_artist}", type='track', limit=1)
    if results['tracks']['items']:
        track_id = results['tracks']['items'][0]['id']
        sp.playlist_add_items(playlist_id=playlist_id, items=[track_id], position=None)
        return True, None
    else:
        return False, f'{current_song} by {current_artist}'

def get_track_id(sp, current_song, current_artist):
    results = sp.search(q=f"track:{current_song} artist:{current_artist}", type='track', limit=1)
    if results['tracks']['items']:
        return results['tracks']['items'][0]['id'], None
    else:
        return None, f'{current_song} by {current_artist}'

def createSpotifyPlaylist():
    # format all playlists
    format_all_playlists()

    # Custom session with timeouts
    session = Session()
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    # Authenticate with Spotify
    auth_manager = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE, 
        requests_timeout=15
    )

    sp = spotipy.Spotify(auth_manager=auth_manager, requests_session=session)

    session.timeout = (5, 15) 
    
    # Get your user ID
    user_id = sp.me()['id']
    
    # prompt user for playlist name
    possible_playlists = os.listdir('Formatted_PlayLists')
    print('\npossible playlists:')
    for index, playlist in enumerate(possible_playlists):
        if playlist.endswith('.txt'):
            print(f' {index} = {playlist}')

    # prompt user for playlist to create
    playlist_index = int(input('Enter the number of the playlist to create: '))
    playlist_file_name = possible_playlists[playlist_index]
    playlist_name = f"NEW_{str(playlist_file_name).replace('.txt', '')}"

    print(f'creating {playlist_name} from file "{playlist_file_name}"...')

    # create playlist
    try:
        new_playlist = sp.user_playlist_create(
            user=user_id, 
            name=playlist_name, 
            public=True, 
            description="created using wetmore's app"
        )
        print(f'created playlist {playlist_name}')
    except SpotifyException as e:
            if e.http_status == 429:  # Too Many Requests
                retry_after = int(e.headers.get("Retry-After", 1))  # Default to 1 second if no header
                print(f"Rate limit hit. Retry after {retry_after} seconds...")
                return
    
    playlist_id = new_playlist['id']

    # add songs to playlist
    songs_not_found = []
    songs_added_successfully = 0
    with open(f'Formatted_PlayLists/{playlist_file_name}', 'r') as formatted_playlist:
        current_song = ""
        current_artist = ""
        tasks = []
        total_songs = 0
        track_ids = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            for index, row in enumerate(formatted_playlist):
                if index % 2 == 0:
                    current_song = row.strip()
                else:
                    current_artist = row.strip()
                    # Submit the task to the executor
                    tasks.append(executor.submit(get_track_id, sp, current_song, current_artist))
                    total_songs += 1
            # Collect results
            total_results_collected = 0
            
            for future in as_completed(tasks):
                current_track_id, song_info = future.result()
                total_results_collected += 1
                if current_track_id is not None:
                    track_ids.append(current_track_id)
                    songs_added_successfully += 1
                else:
                    print(f'{song_info} not found on Spotify')
                    songs_not_found.append(song_info)

                if total_results_collected % 50 == 0:
                    print(f'added {total_results_collected} songs total')

    # Add track IDs to the playlist in batches of 100 to reduce rate limit issues
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i + 100] 
        sp.playlist_add_items(playlist_id=playlist_id, items=batch)

    if songs_not_found != []:
        with open(f"Created_Playlists/{playlist_name}.txt", "w") as songs_info_file:
            songs_info_file.write('SONGS NOT FOUND:\n')
            for song_info in songs_not_found:
                songs_info_file.write(f'{song_info}\n')
    
    shutil.move(f'Formatted_PlayLists/{playlist_file_name}', f'Formatted_but_created_playlists/{playlist_file_name}')
    return

def Clean_Created_Playlists():
    for playlist in os.listdir('Created_Playlists'):
        if playlist.endswith('.txt'):
            with open(f'Created_Playlists/{playlist}', 'r') as created_playlist:
                for line in created_playlist:
                    if line.startswith('ALL'):
                        os.remove(f'Created_Playlists/{playlist}')
                        break
    return


def likeSongsWithinPlaylist():
    # list all playlists
    # Set up authentication with the necessary scope
    # Authenticate with Spotify
    auth_manager = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE, 
        requests_timeout=30
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    Session.timeout = (5, 30)  # Increase the read timeout to 15 seconds
    # Get your user ID
    user_id = sp.me()['id']

    print("getting all playlists...")
    # Get all playlists of the user
    playlists = sp.current_user_playlists()
    track_ids = []

    print("getting all track ids...")
    # Iterate through playlists and collect all track IDs
    while playlists:
        for playlist in playlists['items']:
            results = sp.playlist_items(playlist['id'])
            tracks = results['items']
            while results['next']:
                results = sp.next(results)
                tracks.extend(results['items'])
            for item in tracks:
                track = item['track']
                if track:  # Ensure there's a track object
                    track_ids.append(track['id'])

        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None

    # Add tracks to Liked Songs
    print("adding tracks to liked songs...")
    for track_id in track_ids:
        sp.current_user_saved_tracks_add([track_id])

    print("done")
    return True
