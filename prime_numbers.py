#!/usr/bin/python3
from signal import signal,SIGINT
import sys

def signal_handler(signal, frame):
    print(f'\nimpatient...')
    sys.exit(0)

def prime_seeker():
    result = []
    counter = 0
    try:
        for i in range(1,int(input("How long shall I search prime numbers? Above 10000 can be timeconsuming! Be careful. "))):
            for j in range(1,i + 1):
                if i % j == 0:
                    counter += 1
            if counter == 2:
                result.append(i)
            counter = 0
        print(f'{result}')
    except:
        print(f'Interrupted!')

signal(SIGINT,signal_handler)
prime_seeker()

