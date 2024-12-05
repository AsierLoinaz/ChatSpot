import time
import threading
import random
import pyttsx3
import os
import json
from grove.gpio import GPIO
from grove.button import Button
from grove.display.jhd1802 import JHD1802
from grove.adc import ADC
from smbus2 import SMBus
import paho.mqtt.client as mqtt

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)    # BCM mode for the grovehat connections

# MQTT connections using Mosquitto Broker
address = "10.172.117.154"    # Broker port
topic = "chatspot"            # Topic
client = mqtt.Client()
client.connect(address)

# Questions
questions = [
    "What’s your favorite way to spend a weekend?",
    "Do you prefer coffee or tea, and why?",
    "If you could live anywhere in the world, where would it be?",
    "Do you prefer the mountains or the beach?",
    "What’s the last movie you watched, and how did you like it?",
    "If you could have dinner with any historical figure, who would it be?",
    "What’s your favorite book or author?",
    "What’s a hobby you’ve always wanted to pick up?",
    "What’s your favorite type of music?",
    "Do you play any musical instruments?",
    "What’s the best meal you’ve ever had?",
    "Do you enjoy cooking or baking?",
    "If you could learn any language instantly, which one would it be?",
    "Do you enjoy traveling? Where’s the last place you went?",
    "What’s your dream travel destination?",
    "What’s a fun fact about you that most people don’t know?",
    "Do you enjoy board games or video games?",
    "What’s a TV show you can watch over and over again?",
    "What’s the best gift you’ve ever received?",
    "What’s the best gift you’ve ever given?",
    "If you could only eat one type of cuisine for the rest of your life, what would it be?",
    "Do you prefer staying in or going out on weekends?",
    "What’s your favorite childhood memory?",
    "Do you like pets? Do you have any?",
    "What’s your go-to comfort food?",
    "What’s the most adventurous thing you’ve ever done?",
    "If you won the lottery, what’s the first thing you’d do?",
    "What’s a skill you’re really proud of?",
    "If you could master any sport, which one would it be?",
    "What’s a small thing that makes your day better?",
    "What’s the most interesting thing you’ve learned recently?",
    "Do you believe in any superstitions?",
    "If you could switch jobs for a day, what would you do?",
    "What’s a movie or book that changed your perspective?",
    "What’s your favorite holiday tradition?",
    "If you could time travel, would you go to the past or the future?",
    "What’s your favorite type of dessert?",
    "What’s a song that always gets stuck in your head?",
    "Do you prefer summer or winter?",
    "What’s a habit you’re trying to build or break?",
    "If you could relive any day in your life, which one would it be?",
    "What’s your favorite way to unwind after a long day?",
    "Do you prefer sunrises or sunsets?",
    "What’s a cause you’re passionate about?",
    "If you could start your own business, what would it be?",
    "What’s your favorite way to exercise or stay active?",
    "Do you prefer fiction or non-fiction books?",
    "What’s your favorite type of weather?",
    "What’s a place that holds special meaning for you?",
    "If you could meet any celebrity, who would it be?",
    "What’s your favorite holiday, and why?",
    "Do you prefer movies or TV series?",
    "What’s something new you’ve tried recently?",
    "Do you enjoy art or crafting? What’s something you’ve made?",
    "If you could live in any time period, which one would you choose?",
    "What’s your favorite type of pizza topping?",
    "What’s a quote or saying you live by?",
    "What’s your favorite childhood TV show?",
    "Do you prefer mornings or nights?",
    "What’s a food you’ve never tried but want to?",
    "What’s your favorite ice cream flavor?",
    "Do you prefer reading physical books or e-books?",
    "What’s your dream job?",
    "What’s a tradition from your culture that you love?",
    "What’s the most inspiring thing you’ve heard recently?",
    "What’s a skill you wish you had?",
    "Do you prefer cats or dogs?",
    "What’s your favorite way to celebrate your birthday?",
    "If you could visit any planet, which one would you choose?",
    "What’s your favorite thing about your hometown?",
    "What’s a game you’re really good at?",
    "If you could invent anything, what would it be?",
    "What’s the best concert you’ve ever been to?",
    "What’s a dish you cook really well?",
    "What’s your favorite mode of transportation?",
    "What’s a tradition you’d love to start?",
    "What’s a city or country you’d love to live in?",
    "What’s the best advice you’ve ever received?",
    "What’s your favorite type of flower?",
    "Do you enjoy gardening or being in nature?",
    "What’s a topic you could talk about for hours?",
    "If you could design your dream home, what would it look like?",
    "What’s the best compliment you’ve ever received?",
    "Do you prefer sweet or savory snacks?",
    "What’s a memory that always makes you smile?",
    "What’s your favorite sports team or player?",
    "What’s the most spontaneous thing you’ve ever done?",
    "What’s a challenge you’re proud of overcoming?",
    "Do you prefer shopping online or in stores?",
    "What’s something you’ve built or assembled yourself?",
    "What’s a recipe you’d like to perfect?",
    "What’s your favorite season, and why?",
    "What’s a TV series you’ve binge-watched recently?",
    "What’s your favorite way to spend a lazy day?",
    "What’s a place you’d love to visit again?",
    "Do you believe in luck or fate?",
    "What’s your favorite type of sandwich?",
    "What’s a fun tradition your family has?",
    "What’s your dream vacation activity?"
]

# Grove pin variables selection
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button 1: Starting conversation
button1 = GPIO.input(22)

GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button 2: Ask question
button2 = GPIO.input(24)

GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button 3: Terminate conversation
button3 = GPIO.input(26)

# Screen LED inicialization
bus = SMBus(1) 
RGB = 0x62
TEXT = 0x3e
lcd = JHD1802()

# Potentiometer inicialization
adc = ADC() 
POT = 0
stopVol = False

# Ultrasound threshold
ultrasound = 5 

# Thread to be able to change the volumen at anytime (playing a question, actioning a button,..)
volThread = threading.Thread(target=adjustVol, daemon=True)  
volThread.start()

# TTS engine inicialization
ttsEngine = pyttsx3.init()
ttsEngine.setProperty('rate', 100)

# For button logic and question time duration logic
userWait = False 
waitStart = 0
questionStart = None
questionEnd = 0
questionsDict = {}

# Code to show the question in the RGB LCD screen when pressing button 2
def showQuestion(question):
    lcd.clear()
    if len(question) <= 16:
        lcd.setCursor(0,0)
        lcd.write(question)
        time.sleep(2)
    else:
        for i in range(len(question) -15):
            lcd.setCursor(0,0)
            lcd.write(question[i:i+16])
            time.sleep(0.2)
        lcd.setCursor(0,0)
        lcd.write(question[-16:])

# Code to play and show the question and save it for sending it to the broker
def ask():
    question = random.choice(questions) 
    playAudio(question)
    showQuestion(question)
    print("Question:", question)
    return question

# Code to adjust the volumen of the speaker
def adjustVol():
    while not stopVol:
        value = adc.read(POT)
        volume = int((value / 1023) * 100) # Change the volumen to %
        os.system(f"amixer sset 'Master' {volume}% > /dev/null 2>&1") # Show the actual volumen from 0% to 100%
        time.sleep(0.1)

# Code to TTS the question using the speaker
def playAudio(question):
    ttsEngine.say(question)
    ttsEngine.runAndWait()

# Code to set the possible colors in the RGB LCD screen
def setRGB(r, g, b):
    bus.write_byte_data(RGB, 0, 0)
    bus.write_byte_data(RGB, 1, 0)
    bus.write_byte_data(RGB, 0x08, 0xaa)
    bus.write_byte_data(RGB, 4, r)
    bus.write_byte_data(RGB, 3, g)
    bus.write_byte_data(RGB, 2, b)

# Code to change the RGB LCD screen depending the situation
def changeLed(state):
    if(state == 0):    # Awaiting second user
        print("Led cambiado a blanco")
        setRGB(255, 255, 255)
    elif(state == 1):  # Printing question on the LCD screen
        print("Led cambiado a verde")
        setRGB(0, 255, 0)
    elif(state == 2):
        print("Led cambiado a rojo")    # Terminating conversation and sending the information to the broker
        setRGB(255, 0, 0)
    elif(state == 3):    # Awaiting first user
        print("Led cambiado a morado")
        setRGB(87, 35, 100)
    else:
        print("Led apagado")
        setRGB(0, 0, 0)

# Code to detect the distance of the user to the device
def calcDistance():
    GPIO.setup(ultrasound, GPIO.OUT)
    GPIO.output(ultrasound, GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(ultrasound, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(ultrasound, GPIO.LOW)
    GPIO.setup(ultrasound, GPIO.IN)
    startTime = time.time()
    
    while GPIO.input(ultrasound) == 0:
        startTime = time.time()
    while GPIO.input(ultrasound) == 1:
        stopTime = time.time()

    timeElapsed = stopTime - startTime
    distance = (timeElapsed * 34300) / 2    # Operation to put the distance in centimeters

    return distance

# Mosquitto publisher to the broker
def publishMessage(client, topic, message):
    client.publish(topic, message)
    print(f"Message published in the ChatSpot DB: {message}")

# Prepares and generates the MQTT message as a JSON
def generateMessage(questionsDict, convDuration, waitTime):
    message = {"questionsDict": questionsDict, "convDuration": convDuration, "waitTime":   waitTime}
    return json.dumps(message)

# ChatSpot main execution
try:
    while True:
        changeLed(3)
        button1 = GPIO.input(22)
        if calcDistance() > 30:
            waitStart = time.time()
            print("Waiting for 2 users")
        else:
            waitEnd = time.time() - waitStart
            print("1 user close to the ChatSpot...")
            if button1:
                userWait = True
                changeLed(0)
                convStart = time.time()
            print("2 users close to the ChatSpot, starting conversation...")
            while userWait:
                button2 = GPIO.input(24)
                button3 = GPIO.input(26)
                time.sleep(0.5)
                print("Press the button2 to ask a new question...")
                if button2:
                    changeLed(1)
                    question = ask()
                    lcd.clear()
                    if questionStart is None:
                        questionStart = time.time()
                        questionDuration = questionStart - convStart
                        questionsDict[question] = questionDuration
                        print(questionsDict)
                    else:
                        questionEnd = time.time()
                        questionDuration = questionEnd - questionStart
                        questionStart = questionEnd
                        questionsDict[question] = questionDuration
                        print(questionsDict)
                if button3:
                    print("Terminate conversation...")
                    changeLed(2)
                    time.sleep(3)
                    convEnd = time.time() - convStart
                    userWait = False
                    changeLed(3)
                    msg = generateMessage(questionsDict, convEnd, waitEnd)
                    publishMessage(client, topic, msg)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Keyboard interrupt, cleaning up GPIOs...")
    GPIO.cleanup()
finally:
    print("Deactivating ChatSpot...")
    lcd.clear()
    setRGB(0, 0, 0)
    stopVol = True
    volThread.join()
    GPIO.cleanup()
