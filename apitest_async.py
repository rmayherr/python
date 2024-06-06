import json
from time import perf_counter
import aiohttp
import asyncio


async def make_request(url, params, auth, timeout=6):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, headers=headers, auth=auth,timeout=timeout) as response:
                if response.status != 200:
                    session.raise_for_status()
        await session.close()            
        #return await response.json()
    except aiohttp.ClientConnectorError as e:
        print(f"Request error: {e}")
    return None

async def main(num, url, params, auth):
    try:
        conn = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=conn) as session:
            async with asyncio.timeout(15):
                await asyncio.gather(*[make_request(url, params, auth) for _ in range(num)])
    except TimeoutError:
        print(f"Timeout error occurred.")
    except:
        print(f"Error occurred.")

if __name__ == "__main__":
    num = 1000
    url = "https://zcot.nl.eu.abnamro.com:8153/jr0010a-group-retrieval/V1"
    params = {"userid": "C49677"}
    auth = aiohttp.BasicAuth("C49677", "IPHTL9K3")
    loop = asyncio.get_event_loop()
    start_timer = perf_counter() 
    loop.run_until_complete(main(num, url, params, auth))
    print(f"Elapsed time for {num} requests: {perf_counter() - start_timer} seconds")