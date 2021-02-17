import base64, argparse as ap

def encode(value):
    """
    Get a string and put it in value variable, convert it bytes by using encode() function
    and gives back the base64 encoded bytes as a string by converting it decode() function
    """
    return base64.b64encode(value.encode()).decode()
def decode(value):
    """
    Get a bytes and put it in value variable, decode base64 string and gives back a string
    by convert it to ascii decode() function
    """
    try:
        return base64.b64decode(value).decode()
    except:
        print("It is not base64 encoded string!")
        return ""
def get_arg():
    """
    args = parser.parse_args()
    New format is availbe in python 3.6x
    print(f"Value for -e { vars(args)['encode'] }, value for -d { vars(args)['decode'] }")
    """
    parser = ap.ArgumentParser(description="Base64 encode/decoder")
    """
    Only one arguments can be passed one time
    """
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e','--encode',nargs='?',help='Encode ascii text to base64')
    group.add_argument('-d','--decode',nargs='?',help='Decode base64 txt to ascii')
    return vars(parser.parse_args())

values = get_arg()
if values['encode'] != None:
    print(encode(values['encode']))
elif values['decode'] != None:
    print(decode(values['decode']))

