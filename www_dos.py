import aiohttp
import asyncio
import time
from collections import Counter

wurl = 'https://horus/overtime'
statuses = Counter()

async def get_req(wurl, session):
    global statuses

    async with session.get(wurl) as response:
        statuses[response.status] += 1

async def main(wurls, loop):
    num_of_requests = 2000
    conn = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        await asyncio.gather(*[get_req(wurl, session) for _ in range(num_of_requests)])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    start = time.perf_counter() 
    loop.run_until_complete(main(wurl, loop))
    print(f'Executed in {(time.perf_counter() - start):.4f} seconds')
    for key, value in statuses.items():
        print(f'Status code {key} {value} requests.')
