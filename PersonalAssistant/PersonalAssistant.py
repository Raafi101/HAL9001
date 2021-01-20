#Personal Assistant
#Jarvis AI
#Raafi Rahman

#import modules ===================================================================================
import speech_recognition as sr
import pyttsx3 as tts
import pywhatkit as whatkit
import datetime
import wikipedia as wiki
import random
import json
from json.decoder import JSONDecodeError
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
import os
import sys
import spotipy
import spotipy.util as util
import webbrowser
import base64
import requests
import playSpotify
import getWeather
import geocoder

#Data formatting ==================================================================================
lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('PersonalAssistantModel.h5')

def cleanUpSentence(sentence):
    sentenceWords = nltk.word_tokenize(sentence)
    sentenceWords = [lemmatizer.lemmatize(word) for word in sentenceWords]
    return sentenceWords

def bagOfWords(sentence):
    sentenceWords = cleanUpSentence(sentence)
    bag = [0] * len(words)
    for w in sentenceWords:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predictClass(sentence):
    aBagOfWords = bagOfWords(sentence)
    res = model.predict(np.array([aBagOfWords]))[0]
    TOLERANCE = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > TOLERANCE]

    results.sort(key = lambda x: x[1], reverse = True)
    returnList = []
    for r in results:
        returnList.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return returnList

def getResponse(intentsList, intentsJSON):
    tag = intentsList[0]['intent']
    listOfIntents = intentsJSON['intents']
    for i in listOfIntents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

#Speech --> Text --> Text --> Speech ==============================================================

#Initialize
audioIn = sr.Recognizer()
engine = tts.init()
ready = True

#Assistant voice
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

#Dynamic talk function
def talk(text):
    engine.say(text)
    engine.runAndWait()

#Listen to command
def takeCommand():
    global command
    try:
        with sr.Microphone() as audioSource:
            print('Listening...')
            voice = audioIn.listen(audioSource)
            command = audioIn.recognize_google(voice)
            command = command.lower()
    except:
        takeCommand()

    return command

#Converse via intents
def converse(sentence):
    message = sentence
    intentGuess = predictClass(message)
    response = getResponse(intentGuess, intents)
    if response == "get time":
        getTime()
    elif response == "get date":
        getDate()
    elif response == "get age":
        getAge()
    elif response == "get weather":
        getTheWeather()
    elif response == "get current song":
        getCurrentSong()
    elif response == "skip song":
        skipSong()
    else:
        talk(response)

#What is the time?
def getTime():
    time = datetime.datetime.now().strftime('%I:%M %p')
    hour = time[0:2]
    if hour[0] == '0':
        hour = hour.replace(hour[0],'')
    timeFixed = datetime.datetime.now().strftime(hour + '%M %p')
    talk('It is ' + timeFixed)

#What is the date?
def getDate():
    date = datetime.datetime.now().strftime('%A, %B, %d, %Y')
    talk('it is' + date)

#How old am I?
def getAge():
    datetimeDiff = (datetime.datetime.now() - datetime.datetime(2021, 1, 2))
    talk('I am' + str(datetimeDiff.days // 365) + 'years and' + str(datetimeDiff.days % 365) + 'days old')

#What is the weather?
def getTheWeather():
    location = geocoder.ip('me')
    city = location.city
    weather = getWeather.getCurrentWeather(city)
    talk(weather)

#What song is playing?
def getCurrentSong():
    currentSong = playSpotify.getCurrent()
    talk(currentSong)

#Skip song
def skipSong():
    playSpotify.nextSong()


#RUN THE MACHINE===================================================================================
def runAI(command):

    global ready

    #Play song on spotify
    if 'spotify' in command and 'play' in command:
        newCommand = command.split('play ')[1]
        if ' on spotify' in newCommand:
            newCommand = newCommand.replace(' on spotify', '')
        song = newCommand
        artist = ''
        if ' by ' in newCommand:
            artist = song.split(' by ')[1]
            song = song.split(' by ')[0]
            talk('Playing ' + song + ' by ' + artist)
        else:
            talk('Playing ' + song)
        try:
            playSpotify.playSong(str(song), str(artist))
        except:
            talk('Song not found')

    #add to queue
    elif ('add' in command and ' to queue' in command) or ('add' in command and ' to the queue' in command) or ('play' in command and 'next' in command):
        song = ''
        artist = ''
        if 'play' in command:
            newCommand = command.split('play ')[1]
            newCommand = newCommand.split(' next')[0]
            song = newCommand
        elif 'add' in command:
            newCommand = command.split('add ')[1]
            newCommand = newCommand.split(' to ')[0]
            song = newCommand
        if ' by ' in newCommand:
            artist = song.split(' by ')[1]
            song = song.split(' by ')[0]
            talk('Adding ' + song + ' by ' + artist + ' to the queue')
        else:
            talk('Adding ' + song + ' to the queue')
        try:
            playSpotify.addToQueue(str(song), str(artist))
        except:
            talk('Song not found')

    #Play video/song on youtube
    elif 'play' in command and 'youtube' in command:
        video = command.replace('play ', '')
        video = video.replace(' on youtube', '')
        talk('Playing ' + video)
        whatkit.playonyt(video)

    #Google search
    elif 'search up' in command:
        topic = command.replace('search up', '')
        talk('Searching up ' + topic)
        whatkit.search(topic)

    #Who...
    elif 'who was' in command:
        try:
            topic = command.replace('who was', '')
            info = wiki.summary(topic, 1)
            talk(info)
        except:
            topic = command.replace('who was', '')
            talk("This is what I found on Google.")
            whatkit.search('who was' + topic)

    elif 'who is' in command:
        try:
            topic = command.replace('who is', '')
            info = wiki.summary(topic, 1)
            talk(info)
        except:
            topic = command.replace('who is', '')
            talk("This is what I found on Google.")
            whatkit.search('who is' + topic)

    elif 'who are' in command:
        if 'who are you' in command:
            converse(command)
        else:
            try:
                topic = command.replace('who are', '')
                info = wiki.summary(topic, 1)
                talk(info)
            except:
                topic = command.replace('who are', '')
                talk("This is what I found on Google.")
                whatkit.search('who are' + topic)

    elif 'who were' in command:
        try:
            topic = command.replace('who were', '')
            info = wiki.summary(topic, 1)
            talk(info)
        except:
            topic = command.replace('who were', '')
            talk("This is what I found on Google.")
            whatkit.search('who were' + topic)

    #What...
    elif 'what is' in command:
        if 'your birthday' in command or 'your name' in command or 'your age' in command or 'the date' in command or 'day' in command or 'time' in command or 'weather' in command  or 'temperature' in command:
            converse(command)
        else:
            try:
                topic = command.replace('what is', '')
                info = wiki.summary(topic, 1)
                talk(info)
            except:
                topic = command.replace('what is', '')
                talk("This is what I found on Google.")
                whatkit.search('what is' + topic)

    elif 'what was' in command:
        try:
            topic = command.replace('what was', '')
            info = wiki.summary(topic, 1)
            talk(info)
        except:
            topic = command.replace('what was', '')
            talk("This is what I found on Google.")
            whatkit.search('what was' + topic)

    elif 'what are' in command:
        try:
            topic = command.replace('what are', '')
            info = wiki.summary(topic, 1)
            talk(info)
        except:
            topic = command.replace('what are', '')
            talk("This is what I found on Google.")
            whatkit.search('what are' + topic)

    elif 'what were' in command:
        try:
            topic = command.replace('what were', '')
            info = wiki.summary(topic, 1)
            talk(info)
        except:
            topic = command.replace('what were', '')
            talk("This is what I found on Google.")
            whatkit.search('what were' + topic) 

    #Where...
    elif 'where is' in command:
        topic = command.replace('where is', '')
        talk(topic + ' is located here')
        whatkit.search(command)

    elif 'where was' in command:
        topic = command.replace('where was', '')
        talk(topic + ' was here')
        whatkit.search(command)

    elif 'where are' in command:
        topic = command.replace('where are', '')
        talk(topic + ' are here')
        whatkit.search(command)

    elif 'where were' in command:
        topic = command.replace('where were', '')
        talk(topic + ' were here')
        whatkit.search(command)

    #When is...
    elif 'when' in command:
        if 'is your birthday' or 'were you born' in command:
            converse(command)
        else:
            topic = command
            talk("This is what I found on Google.")
            whatkit.search(topic)

    #How is...
    elif 'how' in command:
        if 'old are you' or 'weather' or 'temperature' in command:
            converse(command)
        else:
            topic = command
            talk("This is what I found on Google")
            whatkit.search(topic)

    #Unexpected command
    else:
        converse(command)
    
    ready = True


#Add pyjokes ("Tell me a joke/fact")
#Start the visual aspect of the project. (Watch Later YT). Use webcam to track your face.
talk("Hello. How can I help you?")
while True:
    command = takeCommand()
    runAI(command)