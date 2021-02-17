from itertools import groupby
def logo(s):
    result = [[s.count(i), i] for i in sorted(set([*s]))]
    ordered_list = sorted([i for i in result], reverse=True)
    counter = 1
    for i in [list(i) for j,i in groupby(ordered_list, lambda x: x[0])]:
        for j in sorted(i):
            if counter < 4:
                print(f'{j[1]} {j[0]}')
                counter += 1
if __name__ == '__main__':
    logo(input())
# qwertyuiopasdfghjklzxcvbnm
