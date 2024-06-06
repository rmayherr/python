import json
from time import perf_counter
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def make_request(url, params, auth, timeout=6):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    try:
        response = requests.post(url, json=params, headers=headers, auth=auth,timeout=timeout, verify=False)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return response.json()
    except requests.exceptions.Timeout:
        print("Timeout error: The request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    return None

"""
def insert_data(url, params, auth, timeout=6):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    try:        
        response = requests.post(url, json=params, headers=headers, auth=auth,timeout=timeout, verify=False)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return response.json()
    except FileNotFoundError:
        print("File not found.")
    except requests.exceptions.Timeout:
        print("Timeout error: The request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}") 
    return None
"""
if __name__ == "__main__":
    num = 200
    start_timer = perf_counter() 
    url = "https://zcot.nl.eu.abnamro.com:8153/jr0010a-group-retrieval/V1"
    params = {"userid": "C49677"}
    auth = HTTPBasicAuth("C49677", "IPHTL9K3")
    for _ in range(num):
        response = make_request(url, params, auth)
        if response:
            pass
            #for i in response['ResultSet Output']:
            #    print(i['GROUPID'])
        else:
            print("Request failed.")
    print(f"Elapsed time for {num} requests: {perf_counter() - start_timer} seconds")