import datetime
import json
from json.decoder import JSONDecodeError
import os
import sys
import spotipy
import spotipy.util as util
import subprocess
from difflib import SequenceMatcher

###This intro code was taken out from "playSong" function =========================================

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

#User Info
user = spotifyObject.current_user()

#Get current device
devices = spotifyObject.devices()
deviceID = devices['devices'][0]['id']


#Functions ========================================================================================

#Helper function to remove unneccessary characters and make all lowercase
def cleanUp(phrase):
    deleteList = ["'", '(', ')', '!', '?', '.', '"', ':', '/', ',']
    newPhrase = phrase.lower()
    for char in newPhrase:
        if char == '-':
            newPhrase = newPhrase.replace(char, ' ')
        if char == '&':
            newPhrase = newPhrase.replace(char, 'and')
        if char in deleteList:
            newPhrase = newPhrase.replace(char, '')
    return newPhrase

#Songs from current search
songList = {}
trackURIs = []

#Search Spotify. Returns song URI
def searchSong(givenSongName, givenArtistName):

    query = ''
    newArtistName = givenArtistName

    if 'the ' in givenArtistName:
        newArtistName = givenArtistName.replace('the ', '')

    if givenArtistName == '':
        query = 'track:' + givenSongName

    elif givenSongName == '':
        query = 'artist:' + newArtistName
        
    else:
        query = 'track:' + givenSongName + ' artist:' + newArtistName

    songResult = spotifyObject.search(q = query, type = 'track')
    songResult = songResult['tracks']['items'][0]['uri']
    return songResult

#Play a song
def playSong(givenSongName, givenArtistName):

    #Call search spotify function
    songURI = searchSong(givenSongName, givenArtistName)
    uriList = [songURI]
    
    #Play song
    spotifyObject.start_playback(deviceID, uris = uriList)

#Gwt current playing song
def getCurrent():

    #Current track
    currentTrack = spotifyObject.current_user_playing_track()
    try:
        artistName = currentTrack['item']['artists'][0]['name']
        trackName = currentTrack['item']['name']
    except:
        currentSong = 'Nothing is playing'
        return currentSong

    currentSong = trackName + " by " + artistName

    return currentSong

#Skip song
def nextSong():
    spotifyObject.next_track()

#Add song to queue
def addToQueue(givenSongName, givenArtistName):
    songURI = searchSong(givenSongName, givenArtistName)
    spotifyObject.add_to_queue(songURI)