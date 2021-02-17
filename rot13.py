from sys import argv

def rot13(message):
    #dictionary from {'a' : 'n'} to {'m' : 'z'}
    wdict = dict(list(zip([chr(i) for i in range(97,110)], [ chr(j) for j in range(110,127)])))
    wdict.update(list(zip([chr(i) for i in range(110,127)], [ chr(j) for j in range(97,110)])))
    result = ""
    for i in message:
        if not (i.isalpha()):
            result += i
        elif (i.isupper()):
            result += wdict[i.lower()].upper()
        elif (i.lower()):
            result += wdict[i]
    return result

def test_rot13():
    assert rot13("test") == "grfg"
    assert rot13("Test") == "Grfg"
    assert rot13("Hello World!") == "Uryyb Jbeyq!"


#print(rot13(argv[1]))
