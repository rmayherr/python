#!/usr/bin/python3
from gtts import gTTS
import pyttsx3


wtext = "gtts_text.txt"

e = pyttsx3.init()
with open(wtext, 'r') as f:
#    r = gTTS(" ".join([i.strip('\n') for i in f.readlines(500)]), )
#    r.save('speech.mp3')
    r = " ".join([i.strip('\n') for i in f.readlines(500)]) 
e.say(r)
e.runAndWait()
