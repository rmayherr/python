#!/usr/bin/python
import glob, sys, subprocess
import time

wfiles = {}
wfilecontent = []
wfilename = ""
wfilecache = []
#Set colored messages
def printColored(msg, color="red"):
    if color == "red":
        print('\x1b[1;37;41m' + msg + '\x1b[0m')
        time.sleep(2)
    if color == "green":
        print('\x1b[6;30;42m' + msg + '\x1b[0m')
        time.sleep(2)
    if color == "blue":
        print('\x1b[6;34;47m' + msg + '\x1b[0m')
        time.sleep(1)
def listDir():
    global wfiles
    counter = 1
    try:
#List files with lst extension current directory
        r = glob.glob('./*.lst',recursive=False)
#If one file found return 1 if more than one return 0
        if len(r) == 0:
            return 1
        else:
            for i in r:
                i = i.split("/")
                wfiles.update({counter : i[1]})
                counter += 1
            return 0
    except:
        printColored("Error occured listing directory!")
#        print(sys.exc_info()())
        return 2
def openFile(wfilename):
    global wfilecontent
    global wfilecache
    try:
#Open file given in wfilename of the function and push the content to wfilecontent and wfilecache list
        f = open(wfilename,"r")
        line = f.readline()
        while line:
            wfilecontent.append(line)
            wfilecache.append(line)
            line = f.readline()
        f.close()
        return 0
    except:
        printColored("Error occured during opening file " + wfilename + "!")
#        print(sys.exc_info())
        return 1
def createFile(filename="store.lst"):
    global wfilename
    wfilename = filename
    try:
#Create file (default filename store.lst)
        f = open(wfilename,"x")
        f.close()
        return 0
    except:
        printColored("Error creating file " + wfilename + "!")
#        print(sys.exc_info())
        return 1
def fileModified(cache_file, original_file):
#Query whether the content modified or not, compare original file content to cache
    if len(set(original_file) ^ set(cache_file)) == 0:
        return False
    else:
        return True
def saveToFile(wfilename):
#Save contents to file
    global wfilecache
    global wfilecontent
    try:
        f = open(wfilename,"w")
        for i in wfilecache:
            i = i.replace('\n','')
            f.write(i + '\n')
        f.close()
        return 0
    except:
        printColored("Error occured during opening file " + wfilename + " for write!")
#            print(sys.exc_info())
        return 1
def printFileCache():
    nl = 1
#Show content by numbering lines
    for i in wfilecache:
        print(str(nl) + "." + i.replace('\n',''))
        nl += 1
#Menu1 functions Add,Delete,Save,Exit
def startMenu1():
    global wfilecache
    global wfilename
#Start menu1
    while True:
        clearScreen()
        printFileCache()
        printColored("[A] Add item [D] Delete item [S] Save [E] Exit",color="blue")
        answer=input("")
#Handle response
        if answer in ("a", "A"):
            printColored("Type a movie name and Press [Enter]",color="blue")
            answer2 = input("")
#Handle response2
            if answer2 != "":
                wfilecache.append(answer2)
            else:
                printColored("Empty line!")
        if answer in ("s", "S"):
            if fileModified(wfilecache,wfilecontent) == False:
                printColored("There is nothing to be changed.",color="blue")
                pass
            else:
                rc = saveToFile(wfilename)
                if rc == 0:
                    printColored("Data have been saved into file " + wfilename + " succesfully.",color="green")
#After saving content into file clear wfilecache variable in order to avoid duplicate saving
                    wfilecache.clear()
#Reopen file fill up wfilecache and wfilecontent variables
                    openFile(wfilename)
                else:
                    printColored("Error occured during saving into file " + wfilename + "!")
                    sys.exit(1)
        if answer in ("e", "E"):
            sys.exit(0)
        if answer in ("d", "D"):
            printColored("Type a line number to delete item and Press [Enter]",color="blue")
            answer2 = input("")
#Handle response2
            if answer2 != "":
                if answer2.isdigit():
                    if int(answer2) in range(1,len(wfilecache) + 1):
                        windex = int(answer2) - 1
                        del wfilecache[windex]
                        printColored("Item has been deleted succesfully.",color="green")
                        clearScreen()
                        printFileCache()
                    else:
                        printColored("Wrong value!")
                else:
                    printColored("Wrong value!")
            else:
                printColored("Empty line!")
        else:
            pass
#Menu2 functions Add,Save,Exit
def startMenu2():
    global wfilecache
    global wfilename
#Start menu2
    while True:
        clearScreen()
        printFileCache()
        printColored("[A] Add item [S] Save [E] Exit",color="blue")
        answer=input("")
#Handle response
        if answer in ("a", "A"):
            printColored("Type a movie name and Press [Enter]",color="blue")
            answer2=input("")
#Handle response2
            if answer2 != "":
                wfilecache.append(answer2)
            else:
                printColored("Empty line!")
        if answer in ("s", "S"):
            if fileModified(wfilecache,wfilecontent) == False:
                printColored("There is nothing to be changed.",color="blue")
                pass
            else:
                rc = saveToFile(wfilename)
                if rc == 0:
                    printColored("Data have been saved into file " + wfilename + " succesfully.",color="green")
#After saving content into file clear wfilecache variable in order to avoid duplicate saving
                    wfilecache.clear()
#Reopen file fill up wfilecache and wfilecontent variables
                    openFile(wfilename)
                else:
                    printColored("Error occured during saving into file " + wfilename + "!")
                    sys.exit(1)
        if answer in ("e", "E"):
            sys.exit(0)
        else:
            pass
def startMenu3():
    global wfilecache
    global wfilename
#If more than one file with lst extension found
    while True:
        clearScreen()
        for key,value in wfiles.items():
            print(str(key) + ". " + value)
        printColored("There are more than one file with lst extension above.Which one do you want to open?",color="blue")
        printColored("Type a valid number and press [Enter] or [C] create new file [E] exit.",color="blue")
        answer = input("")
        if answer in ("c","C"):
            printColored("Type the name of the new file and press [Enter]",color="blue")
            printColored("If you press [Enter] default name will be used [movie_store.lst] [E] exit",color="blue")
            answer2 = input("")
            if answer2 == "":
                rc = createFile()
                if rc == 0:
                    printColored("File movie_store.lst was created.",color="blue")
                    break
                else:
                    printColored("File movie_store.lst was not created!")
                    break
            elif answer2 in ("e","E"):
                sys.exit(0)
            else:
#Create file with the name given
                rc = createFile(filename=answer2)
                if rc == 0:
                    printColored("File " + wfilename + " was created.",color="blue")
                    clearScreen()
                    listDir()
                else:
                    printColored("File " + wfilename + " was not created!")
                    break
        elif answer in ("e","E"):
            sys.exit(0)
        elif answer == "":
            clearScreen()
            pass
#File is selected
        elif answer.isdigit():
            if int(answer) in wfiles:
                rc = openFile(wfiles[int(answer)])
                if rc == 0:
                    printColored("File " + wfiles[int(answer)] + " was opened.",color="green")
                    wfilename = wfiles[int(answer)]
                    listDir()
#Check whether file is empty
                    if len(wfilecontent) == 0:
                        printColored("The file is empty.Please select an action below:",color="blue")
                        startMenu2()
                    else:
                        startMenu1()
                else:
                    printColored("File " + wfiles[int(answer)] + " was not opened.")
                    pass
        else:
            printColored("Wrong answer.Please pick a number.")
            clearScreen()
            pass
def clearScreen():
    proc = subprocess.Popen('clear')
    proc.communicate()

#Start program
if __name__ == "__main__":
    while True:
        clearScreen()
        rc = listDir()
#list filesystem and handle return
        if rc == 0:
#If one file available try to open it
            if len(wfiles) == 1:
                wfilename = wfiles[1]
                printColored("File " + wfilename + " found.",color="blue")
                rc = openFile(wfiles[1])
                if rc == 0:
#Check whether file is empty
                    if len(wfilecontent) == 0:
                        printColored("The file is empty.Please select an action below:",color="blue")
                        startMenu2()
                    else:
                        startMenu1()
                else:
                    printColored("Cannot open file " + wfiles[1] + "!")
                    break
#In case of multiple file found with lst extension
            else:
                startMenu3()
        elif rc == 1:
#If there is no file with lst extension, create one with default name
            rc = createFile()
            if rc == 0:
                printColored("There is no file with lst extension.Default file " + wfilename + " created successfully.",color="green")
                printColored("The file is empty.Please select an action below:",color="blue")
                startMenu2()
            else:
                printColored("File " + wfilename + " could not be created!")
                sys.exit(1)
        else:
            break
            sys.exit(1)
