#!/usr/bin/python3
import random, sys
import subprocess, getopt

uid_min = 0
uid_max = 0
#Linux uid, gid settings
deffile = "/etc/login.defs"
#Input file
infile = "names.csv"
names = []
usernames = []

#Query uid gid range for normal user-creation
def getLimits():
    global uid_min, uid_max
    try:
#Open file for read and save their values
        f = open(deffile,"r")
        for i in f:
            if (i[:7] == "UID_MIN"):
                uid_min = i.split()[1]
            elif (i[:7] == "UID_MAX"):
                uid_max = i.split()[1]
    except:
        print("Error occured during opening " + deffile)
        print(sys.exc_info())
        sys.exit(1)
def generateUid():
    global uid_min, uid_max
#If uid, gid are not 0 then generate one
    if (uid_min != 0 and uid_max != 0):
        return random.randint(int(uid_min), int(uid_max))
    else:
        print("Cannot generate uid number!")
        sys.exit(1)
def getNames():
    global names, usernames
    try:
#Read files which contains the names
        f = open(infile,"r")
        for i in f:
#Remove carriage return
            i = i.rstrip("\n")
#Fill up list with names
            names.append(i)
#Switch to lowercase
            i = i.lower()
            i = i.replace(" ","")
            i = i.replace("'","")
            i = i.replace(".","")
            i = i.replace("-","")
#Separate firstname and lastname by spliting with ','
            fname = i.split(",")[0]
            lname = i.split(",")[1]
#Generate 8length username
            if (len(lname) < 7):
                offset = 8 - len(lname)
                usernames.append(fname[:offset] + lname[:len(lname)])
            else:
                usernames.append(fname[:1] + lname[:7])
#Remove the first line since it is a header
        del usernames[0]
        del names[0]
    except:
        print("Error occured during opening " + infile)
        print(sys.exc_info())
        sys.exit(1)
def createHeader():
#Create header for the riport
	print("{0:<25}{1}{2:^10}{3}{4:^8}".format("User name","|","Uid","|","Userid"))
	print("{0:-<25}{1}{2:-<10}{3}{4:-<8}".format("-","+","-","+","-"))
def createReport():
    getLimits()
    getNames()
    counter = 0
    pagecount = 1
    lastname = names[len(names)-1]
    lastpage = False
#Create riport and separate pages by 50lines and show page number
    for i, j in zip(names, usernames):
        if (len(names) == 1):
           createHeader()
        if (i == lastname):
            lastpage = True
        if (counter == 50):
            print("{0:-<45}".format("-"))
            print("{0:38}{1:>7}".format(" ","page" + str(pagecount)))
            print("\n")
            createHeader()
            print("{0:<25}{1}{2:^10}{3}{4:<8}".format(i,"|",generateUid(),"|",j))
            counter = 0
            pagecount += 1
        else:
            print("{0:<25}{1}{2:^10}{3}{4:<8}".format(i,"|",generateUid(),"|",j))
        if (lastpage == True):
            print("{0:-<45}".format("-"))
            print("{0:38}{1:>7}".format(" ","page" + str(pagecount)))
        counter += 1
def getArguments():
    try:
#Getting arguments by using getopt
        opts, args = getopt.getopt(sys.argv[1:], 'hrc', ['help','report','create'])
    except getopt.error:
        print("Wrong parameter!")
        print("Usage: python3 createusers.py -c or --create to add users")
        print("       python3 createusers.py -r or --report to write console")
        print("       python3 createusers.py -h or --help to print help")
        sys.exit(1)
    for i, j  in opts:
        if i in ('-h', '--help'):
            printHelp()
        elif i in ('-r', '--report'):
            createReport()
        elif i in ('-c', '--create'):
           addUsers()
def printHelp():
        print("Usage:")
        print("       python3 createusers.py -r or --report to write console")
        print("       python3 createusers.py -h or --help to print help")
def addUsers():
    getLimits()
    getNames()
    if (len(names) == 0 or len(usernames) == 0):
        print("null")
    else:
#Run linux command
        for i, j in zip(names, usernames):
            s = subprocess.Popen(['sudo', 'useradd','-M', '-c', '' + i + '', '-u','' + str(generateUid())  + '', '' + j + '' ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate(0)
getArguments()
