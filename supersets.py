import sys

r1 = set(sys.stdin.readline().strip().split(' '))
for i in range(int(sys.stdin.readline())):
    r2 = set(sys.stdin.readline().strip().split(' '))
    if len(r2 - r1) != 0:
        print(f'False')
        sys.exit(0)
    r2 = set()
print(f'True')

