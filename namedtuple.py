from collections import namedtuple
import sys

def avg_marks_manual_input():

    l = int(input("How many times?"))
    r = namedtuple('r',input("Headers?").split(' '),rename=True)
    a = [r._make(input().split(' ')) for i in range(l)]
    print(f'{sum([int(i.marks) for i in a]) / l:.2f}')

first_line = sys.stdin.readline()
r = namedtuple('r',sys.stdin.readline(),rename=True)
a = [r._make((' '.join(sys.stdin.readline().strip().split())).split(' ')) for i in range(int(first_line))]
print(f'{sum([int(i.MARKS) for i in a]) / int(first_line):.2f}')
