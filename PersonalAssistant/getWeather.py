import datetime
import json
import requests
from json.decoder import JSONDecodeError
import os
import sys

def getCurrentWeather(cityName):
    # API key 
    api_key = "5b7b9bd609cc70d9bcb149f6c38c9d3f"
    
    # base_url variable to store url 
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    
    # complete_url variable to store 
    # complete url address 
    complete_url = base_url + "appid=" + api_key + "&q=" + str(cityName) + "&units=imperial"
    
    # get method of requests module 
    # return response object 
    response = requests.get(complete_url) 
    
    # json method of response object  
    # convert json format data into 
    # python format data 
    x = response.json() 
    
    # Now x contains list of nested dictionaries 
    # Check the value of "cod" key is equal to 
    # "404", means city is found otherwise, 
    # city is not found 
    if x["cod"] != "404": 
    
        # store the value of "main" 
        # key in variable y 
        y = x["main"] 
    
        # store the value corresponding 
        # to the "temp" key of y 
        current_temperature_min = y["temp_min"] 

        # store the value corresponding 
        # to the "temp" key of y 
        current_temperature_max = y["temp_max"] 

        # store the value corresponding 
        # to the "temp" key of y 
        current_temperature = y["temp"] 
    
        # store the value corresponding 
        # to the "pressure" key of y 
        current_pressure = y["pressure"] 
    
        # store the value corresponding 
        # to the "humidity" key of y 
        current_humidiy = y["humidity"] 
    
        # store the value of "weather" 
        # key in variable z 
        z = x["weather"] 
    
        # store the value corresponding  
        # to the "description" key at  
        # the 0th index of z 
        weather_description = z[0]["description"] 
    
        # print following values 
        return ("Today is " + str(weather_description) +
            " The current temperature is " + str(current_temperature) + " degrees" +
            " with a low of " + str(current_temperature_min) + " degrees" +
            " and a high of " + str(current_temperature_max) + " degrees") 
    
    else: 
        print(" City Not Found ") 