import argparse as ap

def converter(number):
    result = ""
    number = str(number)
    roman_values = {
                    1 : 'I',
                    5 : 'V',
                    10 : 'X',
                    50 : 'L',
                    100 : 'C',
                    500 : 'D',
                    1000 : 'M'
                }
    def four_digits():
        nonlocal result
        nonlocal number
        if number[0] == '1' and number[1:] == '000':
            result += roman_values[1000]
        else:
            result += roman_values[1000] * int(number[0])
    def three_digits():
        nonlocal result 
        nonlocal number
        if number[1] != '0':
            if number[1] == '4':
                result += roman_values[100] + roman_values[500]
            elif number[1] == '9':
                result += roman_values[100] + roman_values[1000]
            elif number[1] == '1' and number[2:] == '00':
                result += roman_values[100]
            elif number[1] == '5' and number[2:] == '00':
                result += roman_values[500]
            else:
                if number[1] in ['1','2','3','4']:
                    result += roman_values[100] * int(number[1])
                elif number[1] in ['6','7','8']:
                    result += roman_values[500] + (roman_values[100] * (int(number[1]) - 5))
    def two_digits():
        nonlocal result
        nonlocal number
        if number[2] != '0':
            if number[2] == '4':
                result += roman_values[10] + roman_values[50]
            elif number[2] == '9':
                result += roman_values[10] + roman_values[100]
            elif number[2] == '1' and number[3] == '0':
                result += roman_values[10]
            elif number[2] == '5' and number[3] == '0':
                result += roman_values[50]
            else:
                if number[2] in ['1','2','3','4']:
                    result += roman_values[10] * int(number[2])
                elif number[2] in ['6','7','8']:
                    result += roman_values[50] + (roman_values[10] * (int(number[2]) - 5))
    def one_digit():
        nonlocal result
        nonlocal number
        if number[3] == '4':
                result += roman_values[1] + roman_values[5]
        elif number[3] == '5':
                result += roman_values[5]
        elif number[3] == '9':
                result += roman_values[1] + roman_values[10]
        else:
            if number[3] in ['1','2','3','4']:
                result += roman_values[1] * int(number[3])
            elif number[3] in ['6','7','8']:
                result += roman_values[5] + (roman_values[1] * (int(number[3]) - 5))

    if len(number) == 4:
        four_digits()
        three_digits()
        two_digits()
        one_digit()
    elif len(number) == 3:
        number = number.zfill(4)
        three_digits()
        two_digits()
        one_digit()
    elif len(number) == 2:
        number = number.zfill(4)
        two_digits()
        one_digit()
    elif len(number) == 1:
        number = number.zfill(4)
        one_digit()
    return result

parser = ap.ArgumentParser(description="""
            Program converts an arabic number to roman number. Add your desired number as an argument.
                                        """)
parser.add_argument('num',help="Integer value between 1 and 4000",metavar="number",type=int,nargs=1)
r = vars(parser.parse_args())
if r['num'][0] in range(1,4001):
    print(converter(r['num'][0]))
else:
    parser.print_help() 
