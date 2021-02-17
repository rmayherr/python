import argparse as ap

parser = ap.ArgumentParser("Description of argpars.py")
parser.add_argument('-g','--get',nargs='?',help='Application get the time')
parser.add_argument('-s','--set',nargs='?',help='Setting time')
args = parser.parse_args()
#vars command creates a dictionary from  Namesspace
print("Value for get {get}, value for set {set}".format(**vars(args)))
#New format is availbe in python 3.6x
print(f"Value for get { vars(args)['get'] }, value for set { vars(args)['set'] }")



