def fib(n):
    if n <= 1:
        return n
    else:
        return fib(n-1) + fib(n-2)
inp = int(input("Give me a positive integer:"))
for i in range(inp):
    if fib(i) >= inp:
        break
    else:
        print(fib(i))

