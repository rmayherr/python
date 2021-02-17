def timeConversion(s):
    if (s.split(':')[2][2:] == 'AM'):
        if (s.split(':')[0] == '12'):
            return '00' + s[2:-2]
        else:
            return s[:-2]
    else:
        if (s.split(':')[0] == '12'):
            return s[:-2]
        return str(int(s[:2]) + 12) + s[2:-2]

print(timeConversion('07:05:45AM'))
print(timeConversion('12:05:45AM'))
print(timeConversion('07:05:45PM'))
print(timeConversion('12:05:45PM'))

