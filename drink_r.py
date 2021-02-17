#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import sys
piak = ['Cola', 'Whisky', 'Beer', 'Cancel']  # this is an Array
prize = ['120', '430', '250']
print("1.) "+piak[0]+"\n2.) "+piak[1]+"\n3.) "+piak[2]+"\n4.) "+piak[3])


def forint(x):
    return("--------------\nprize: "+ x +" Ft,-\n")


while True:
    try:
        pia = input("\nChoose a drink:\n    1 - 2 - 3 - 4: ")
        pia = int(pia)
    except:
        print("It is not a number!")
        if pia == "Exit":
            print("You entered Exit.Bye.")
            sys.exit(0)
        continue
    if pia == 1:
        print("\n"+piak[0]+" is your choice\n"+forint(prize[0]))
    elif pia == 2:
        print("\n"+piak[1]+" is your choice\n"+forint(prize[1]))
    elif pia == 3:
        print("\n"+piak[2]+" is your choice\n"+forint(prize[2]))
    elif pia == 4:
        print("\n"+piak[3]+"\nWe respect your choice.")
    else:
        print("Bad decision....try again.")
        continue
