import numpy as np

first_ = input().split(" ")
arr_a, arr_b = np.empty((0,int(first_[2])), int), np.empty((0, int(first_[2])), int)
for i in range(int(first_[0])):
        arr_a = np.append(arr_a, np.array([list(map(int, list(input().split(' '))))]), axis = 0)
for j in range(int(first_[1])):
        arr_b = np.append(arr_b, np.array([list(map(int, list(input().split(' '))))]), axis = 0)
print(f'{np.concatenate((arr_a, arr_b), axis = 0)}')


