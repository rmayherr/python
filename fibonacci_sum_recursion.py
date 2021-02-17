from  multiprocessing import Process, Pool, cpu_count
import timeit
import os

def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def caller_func(n):
    print(fib(n))


def multiprocessing_func(n):
    jobs = []
    for i in range(10):
        p = Process(target=fib, args=(n,), name='fibonacci_' + str(i))
        jobs.append(p)
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()

def multiprocessing_pool_func(n):
    with Pool(10) as p:
        p.map(fib, [n] * 10)

if __name__ == '__main__':
    os.system('clear')
    number = int(input('Give me an end number until I can calculate the sum of Fibonacci numbers: '))
    print(f'Using {cpu_count()} cpu core')
    print(f"Function is running 10 times using multiprocessing Pool, average execution time is : "
          f"{timeit.timeit(stmt='multiprocessing_pool_func(number)', setup='from __main__ import multiprocessing_pool_func, number', number=1)} seconds")
    print(f"Function is running 10 times using multiprocessing Process, average execution time is : "
          f"{timeit.timeit(stmt='multiprocessing_func(number)', setup='from __main__ import multiprocessing_func, number', number=1)} seconds")
    print(f"Function is running 10 times, average execution time is : "
          f"{timeit.timeit(stmt='fib(number)', setup='from __main__ import fib, number', number=10)} seconds")
    print(f'{fib(number)}')
