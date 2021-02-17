#!/usr/bin/env python3
import requests, sys, traceback, subprocess, tempfile, getopt
from bs4 import BeautifulSoup

wurl = "https://developer.ibm.com/javasdk/support/zos/"

def download(url):
    """
    Download webpage from specific url
    """
#Download from url
    try:
        r = requests.get(url,allow_redirects = True, timeout = 10)
#When url doesn't contain the filename to be downloaded you can check it via 'content-disposition'
    #print(r.headers.get('content-disposition'))
#Check content-type whether text/html type and html status code 200 is OK
        wtype = r.headers.get('content-type').split(';')
        if wtype[0] == "text/html" and r.status_code == 200:
#Return downloaded page
            return r.text
    except:
        printColor("Error occured in download()!")
        traceback.print_exc()
        sys.exit(1)
def parse_page(content):
    data = []
    counter = 1
    tmp = []
    s = BeautifulSoup(content,'html.parser')
    for i in s.find_all('td'):
        if counter == 5:
            counter = 1
            data.append(tmp)
            tmp = []
        counter += 1
        tmp.append(i.text)
    return data
def print_data(data):
    print("\x1b[1;37;42m {sdk:<29}| {level:<70} \x1b[0m".format(sdk="SDK version",level="Latest build level"))
    print("{:-^103}".format("-"))
    for i in data:
        #print("{0:<30}|{1:<80}".format(i[0].encode('utf-8'),i[1].encode('utf-8').lstrip()))
        print("{0:<30}|{1:<80}".format(i[0],i[1].lstrip()))
def getArguments():
    try:
#Getting arguments by using getopt
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['html'])
    except getopt.error:
        print("Wrong parameter!")
        sys.exit(1)
    for i, j  in opts:
        if i in ('-h', '--html'):
            print("Usage: \n\t python3 javaptf_bs4.py \n\t or \n\t python3 javaptf_bs4.py --html")
            sys.exit(0)
    else:
        a = parse_page(download(wurl))
        print_data(a)
if __name__ == "__main__":
    getArguments()
