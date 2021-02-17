import random as r

def rand_char(wlength,level="s"):
    counter = 0
    wpassword = ""
    while counter < wlength:
        if level == "s":
            if wpassword != "":
                tmp = chr(r.randrange(33,127))
                if wpassword[-1:] == tmp:
                    continue
                elif tmp in ["<",">","^","*","$","%","~","`","|"," ","'","\\"]:
                    continue
                else:
                     wpassword += tmp
                     counter += 1
            else:
                tmp = chr(r.randrange(33,127))
                if tmp in ["<",">","^","*","$","%","~","`","|"," ","'","\\"]:
                    continue
                else:
                     wpassword += tmp
                     counter += 1
        elif level == "n":
            tmp = r.randrange(48,122)
            #[0-9] or [A-Z] or [a-z]
            if tmp in range(48,58) or tmp in range(65,91) or tmp in range(97,123):
                wpassword += chr(tmp)
                counter += 1
    return wpassword
def length_check():
    wlength = input("\tWhat is the length of password? [8-16] (default is 8) ")
    try:
        if wlength == "":
            wlength = 8
            return wlength
        elif int(wlength) not in range(8,17):
            return "Null"
        else:
            return int(wlength)
    except ValueError:
        return "Null"
def level_check():
    wlevel = input("\tHow strong is the password? [n] normal - [s] strong (default is strong) ")
    try:
        if wlevel == "":
            wlevel = "s"
            return wlevel
        elif wlevel == "n":
            return wlevel
        elif wlevel == "s":
            return wlevel
        else:
            return "Null"
    except ValueError:
        return "Null"
if __name__ == '__main__':
    while True:
        wlength = length_check()
        if wlength == "Null":
            print("\tWrong input!")
            continue
        else:
            wlevel = level_check()
            if wlevel == "Null":
                print("\tWrong input!")
                continue
            else:
                if wlevel == 'n':
                    print(rand_char(wlength,level="n"))
                    break
                elif wlevel == 's':
                    print(rand_char(wlength))
                    break

