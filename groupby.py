from itertools import groupby 
import sys

for key, group in groupby(sys.stdin.readline()):
    print(f'{key} {list(group)}')
