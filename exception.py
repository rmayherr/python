#!/usr/bin/python3
import random,sys

class Picike(Exception):
    """
    Custom exception
    """
    pass

class Nagyonnagy(Exception):
    """
    Custom exception
    """
    pass

a = random.randrange(1,10)

while True:
    try:
        value = input("Mondj egy számot 1-től 10-ig: ")
        if int(value) == a:
            print("Szééééép")
            break
        elif int(value) > a:
            raise Nagyonnagy
        elif int(value) < a:
            raise Picike
        else:
            pass
    except Nagyonnagy:
        print("Fölélőttél, próbáld újra!")
    except Picike:
        print("Ez meg kevesebb, póbáld újra!")
    except:
        print("\nValami itt nagyon nem jó!Ha menni akarsz hát menj.")
        sys.exit(1)

