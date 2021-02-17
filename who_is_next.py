import sys

def who_is_next(string, number):
    pos = 1
    for i in range(0,30):
        for j in range(0,len(string)):
            for k in range(0,pow(2,i)):
                if (number == pos):
                    #print(f'{string[j]}')
                    return string[j]
                    sys.exit(0)
                pos += 1

def who_is_next2(string, number):
    for i in range(number):
        first_item = string.pop(0)
        string.extend(list([first_item, first_item]))
        print(string)
    return "".join(string[-1:])

def test_who_is_next():
    assert who_is_next(["Sheldon", "Leonard", "Penny", "Rajesh", "Howard"], 1) == "Sheldon"
    assert who_is_next(["Sheldon", "Leonard", "Penny", "Rajesh", "Howard"], 52) == "Penny"
#    assert who_is_next(["Sheldon", "Leonard", "Penny", "Rajesh", "Howard"], 7230702951) == "Leonard"

