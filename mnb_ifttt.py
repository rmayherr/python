#!/usr/bin/env python3
import requests, sys, traceback, os
from bs4 import BeautifulSoup

wurl = "https://mnb.hu/arfolyamok"

def download(url):
    try:
        r = requests.get(url,allow_redirects = True, timeout = 10)
        wtype = r.headers.get('content-type').split(';')
        if wtype[0] == "text/html" and r.status_code == 200:
            return r.text
    except:
        print("Error occured in download()!")
        traceback.print_exc()
        sys.exit(1)
def parse_page(content):
    s = BeautifulSoup(content,'html.parser')
    counter = 1
    result = []
    wdate = s.find("th", { 'class' : 'head' })
    result.append(wdate.get_text().encode('utf-8'))
    for i in s.find_all("td", {'class' : ['valute', 'value']}):
        if counter == 7:
            break
        result.append(i.get_text())
        counter += 1
    return result
def send_data_to_ifttt(data):
    url = "https://maker.ifttt.com/trigger/trigger1/with/key/gDnBibAph6xk4EJtTz8LXTp_4OpBAJL6HJyAzmQ23nt"
    params = {}
    params["value1"] = data[1] + " " + data[2] + "HUF\n" +\
                         data[3] + " " + data[4] + "HUF\n" +\
                         data[5] + " " + data[6] + "HUF\n"
    params["value2"] = data[0].decode() + "MNB legfrissebb hivatalos deviza árfolyamai"
    r = requests.post(url, data = params)
    if r.status_code == 200:
        return 0
    else:
        print("Bad request. Response code " + r.status_code)
        return 1

if __name__ == "__main__":
    send_data_to_ifttt(parse_page(download(wurl)))

