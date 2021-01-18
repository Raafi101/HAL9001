#Personal Assistant Training Model

import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD
import pandas as pd

#Intents set up
lemmatizer = WordNetLemmatizer()

intents = json.loads(open('intents.json').read())

words = []
classes = []
documents = []
ignoredLetters = ['?', '!', '.', ',']

for intent in intents['intents']:
    for pattern in intent['patterns']:
        wordList = nltk.word_tokenize(pattern)
        words.extend(wordList)
        documents.append(((wordList), intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = [lemmatizer.lemmatize(word) for word in words if word not in ignoredLetters]
words = sorted(set(words))

classes = sorted(set(classes))

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

#Model details (preprocessing)

training = []
outputEmpty = [0] * len(classes)

for document in documents:
    bag = []
    wordPatterns = document[0]
    wordPatterns = [lemmatizer.lemmatize(word.lower()) for word in wordPatterns]
    for word in words:
        bag.append(1) if word in wordPatterns else bag.append(0)

    outputRow = list(outputEmpty)
    outputRow[classes.index(document[1])] = 1
    training.append([bag, outputRow])

random.shuffle(training)
training = np.array(training)

trainX = list(training[:, 0])
trainY = list(training[:, 1])

#Model

model = Sequential()
model.add(Dense(128, input_shape = (len(trainX[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(trainY[0]), activation='softmax'))

StochasticGradientDescent = SGD(lr=0.01, decay = .000001, momentum=0.9, nesterov=True)

model.compile(loss = 'categorical_crossentropy', optimizer=StochasticGradientDescent, metrics = ['accuracy'])

hist = model.fit(np.array(trainX), np.array(trainY), epochs = 200, batch_size = 5, verbose=1)

"""
model.save('PersonalAssistantModel.h5', hist)
"""