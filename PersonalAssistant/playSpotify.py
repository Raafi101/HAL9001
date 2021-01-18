import datetime
import json
from json.decoder import JSONDecodeError
import os
import sys
import spotipy
import spotipy.util as util
import subprocess

def playSong():
    search = True
    songSearch = True

    #Spotify app client ID and secret
    client_id = 'ad0f370ae2b74a2885d8af3f12907c6a'
    client_secret = '9bbc2b904c4845878949f1b3a20c618a'
    os.environ["SPOTIPY_CLIENT_ID"]=client_id
    os.environ["SPOTIPY_CLIENT_SECRET"]=client_secret
    os.environ["SPOTIPY_REDIRECT_URI"]="http://google.com/"

    # Get the username from terminal
    username = "rafhay101" #input(str("Enter Spotify Username: "))
    scope = 'user-read-private user-read-playback-state user-modify-playback-state'

    #Get token
    try:
        token = util.prompt_for_user_token(username, scope)
    except:
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope)

    #Spotify ID: rafhay101?si=BGLiJMC0QUOFVEaPQ4VMpw

    #Create spotify object
    spotifyObject = spotipy.Spotify(auth = token)

    #Get current device
    devices = spotifyObject.devices()
    print(len(devices['devices']))
    deviceID = devices['devices'][0]['id']

    #Current track
    currentTrack = spotifyObject.current_user_playing_track()
    print(json.dumps(currentTrack, sort_keys=True, indent=4))
    if currentTrack != None:
        artistName = currentTrack['item']['artists'][0]['name']
        trackName = currentTrack['item']['name']
        print('Currently playing ' + trackName + " by " + artistName)

    #User Info
    user = spotifyObject.current_user()
    displayName = user['display_name']
    followers = user['followers']['total']

    while search:
        print('Welcome to Spotipy ' + displayName + '!')
        print('You have ' + str(followers) + ' followers!')
        query = input("Search for an artist: ")
        if query == 'exit':
            search = False
            break
        print('Searching ' + query + '.')
        songSearch = True
        results = spotifyObject.search(query, 1, 0, 'artist')
        print(json.dumps(results, sort_keys=True, indent=4))

        #Artist details
        artist = results['artists']['items'][0]
        print(artist['name'])
        print(str(artist['followers']['total']) + " followers")
        print("Genre: " + artist['genres'][0])
        artistID = artist['id']

        #Album and track details
        trackURIs = []
        trackArt = []
        c = 0

        #Get album data
        albumResults = spotifyObject.artist_albums(artistID)
        albumResults = albumResults['items']

        for album in albumResults:
            print("Album: " + album['name'])
            albumID = album['id']
            albumArt = album['images'][0]['url']

            #get tracks data
            trackResults = spotifyObject.album_tracks(albumID)
            trackResults = trackResults['items']

            for track in trackResults:
                print(str(c) + ": " + track['name'])
                trackURIs.append(track['uri'])
                trackArt.append(albumArt)
                c += 1
        
        #See album art
        while songSearch:
            songSelect = input("Enter a song number to play: ")
            if songSelect == 'x':
                break
            if songSelect == 'exit':
                search = False
                break
            if songSelect == 'back':
                songSearch = False
                break
            queue = []
            queue.append(trackURIs[int(songSelect)])
            spotifyObject.start_playback(deviceID, None, queue)