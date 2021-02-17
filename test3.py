#!/usr/bin/env python3
import sys, getopt
#print(sys.argv)i
wout = ""
try:
    opts, args = getopt.getopt(sys.argv[1:], 'hrc', ['help','riport','create'])
except getopt.error:
    print("wrong parameter")
    print("Usage: -h or --help ")
    sys.exit(1)
for i, j  in opts:
    if i in ('-h', '--help'):
        print("Help...")
    elif i in ('-r', '--riport'):
        print("Run riport...")
    elif i in ('-c', '--create'):
        print("Create riport...")
