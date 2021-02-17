
#!/usr/bin/env python3
import requests, sys, traceback, re
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
def print_data(data):
    #header = 'MNB legfrissebb hivatalos deviza' + '\xe1' + 'rfolyamai'
    header = 'MNB legfrissebb hivatalos deviza árfolyamai'
    print(f'\t{header} {data[0].decode()}')
    print(f'\t{data[1]:<4} {data[2]:<6} HUF')
    print(f'\t{data[3]:<4} {data[4]:<6} HUF')
    print(f'\t{data[5]:<4} {data[6]:<6} HUF')

if __name__ == "__main__":
    print_data(parse_page(download(wurl)))

