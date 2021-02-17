import asyncio
import time
import concurrent.futures as cf 
import random


async def func():
    #async def func(n):
    #return [n ** i for i in range(2,22,2)]
    return [random.randint(1,1000000) for i in range(1,1000000)]

async def main(*args):
    """
    await passes function control back to the event loop

    async def g():
        Pause here and come back to g() when f() is ready
        r = await f()
        return r
    """
    #coros = [func(i) for i in args]
    coros = [func() for i in range(2)]
    r = await asyncio.gather(*coros)
    print(r)

if __name__ == '__main__': 
    start = time.perf_counter()
    #a = [2, 3, 4]
    #asyncio.run(main(*a))
    asyncio.run(main())
    print(f'executed {(time.perf_counter() - start):.4f}')
