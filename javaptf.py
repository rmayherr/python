#!/usr/bin/env python3
import requests, sys, traceback, subprocess, tempfile, getopt

wurl = "https://developer.ibm.com/javasdk/support/zos/"
wfile = ""

def printColor(msg):
    print('\x1b[1;37;41m' + msg + '\x1b[0m')
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
def cut_file_java8(filename,html="no"):
    """
    Edit downloaded content, gain Java 8 values from it by using linux commands
    """
    wresult = []
    try:
#Call linux commands to edit downloaded webpage, cut Java 8 related stuff
        p1 = subprocess.Popen(['cat',filename],stdout=subprocess.PIPE,shell=False)
        p2 = subprocess.Popen(['grep','-n','IBM SDK for z/OS, Java Technology Edition, Version 8'],stdin=p1.stdout,stdout=subprocess.PIPE,shell=False)
        p3 = subprocess.Popen(['cut','-d',''':''','-f1' ],stdin=p2.stdout,stdout=subprocess.PIPE,shell=False)
        p4 = subprocess.Popen(['tail','-n','1'],stdin=p3.stdout,stdout=subprocess.PIPE,shell=False)
        woutp4, werrp4 = p4.communicate()
        woutp4 = woutp4.decode('utf-8')
        wstring1 = woutp4.strip() + ",+40p"
        p5 = subprocess.Popen(['sed','-n','-e',wstring1,filename],stdout=subprocess.PIPE,shell=False)
        p6 = subprocess.Popen(['grep','<td>'],stdin=p5.stdout,stdout=subprocess.PIPE,shell=False)
        woutp6, werrp6 = p6.communicate()
        wresult = woutp6.decode('utf-8').split("\r")
        if html == "no":
            print("{0:<23}\t{1:<50}\n{2:<23}\t{3:<50}".format(
                                                            wresult[0][5:-5],
                                                            wresult[1][23:-5],
                                                            wresult[3][6:-5],
                                                            wresult[4][23:-5]
                                                             ))
        elif html == "yes":
            wresult = "<p font-family: Arial> {0:<23}\t{1:<50}\n <br> {2:<23}\t{3:<50} \n </p>\n".format(
                                                            wresult[0][5:-5],
                                                            wresult[1][23:-5],
                                                            wresult[3][6:-5],
                                                            wresult[4][23:-5]
                                                             )
            return wresult

    except:
        printColor("Error occured in cut_file_java8()!")
        traceback.print_exc()
def cut_file_java7(filename,html="no"):
    """
    Edit downloaded content, gain Java 7 values from it by using linux commands
    """
    wresult = []
    try:
#Call linux commands to edit downloaded webpage, cut Java 7 related stuff
        p1 = subprocess.Popen(['cat',filename],stdout=subprocess.PIPE,shell=False)
        p2 = subprocess.Popen(['grep','-n','IBM SDK for z/OS, Java Technology Edition, Version 7'],stdin=p1.stdout,stdout=subprocess.PIPE,shell=False)
        p3 = subprocess.Popen(['cut','-d',''':''','-f1' ],stdin=p2.stdout,stdout=subprocess.PIPE,shell=False)
        p4 = subprocess.Popen(['tail','-n','1'],stdin=p3.stdout,stdout=subprocess.PIPE,shell=False)
        woutp4, werrp4 = p4.communicate()
        woutp4 = woutp4.decode('utf-8')
        wstring1 = woutp4.strip() + ",+40p"
        p5 = subprocess.Popen(['sed','-n','-e',wstring1,filename],stdout=subprocess.PIPE,shell=False)
        p6 = subprocess.Popen(['grep','<td>'],stdin=p5.stdout,stdout=subprocess.PIPE,shell=False)
        woutp6, werrp6 = p6.communicate()
        wresult = woutp6.decode('utf-8').split("\r")
        if html == "no":
            print("{0:<23}\t{1:<50})\n{2:<23}\t{3:<50}".format(
                                                            wresult[0][5:-5],
                                                            wresult[1][23:-7],
                                                            wresult[3][6:-5],
                                                            wresult[4][23:-5]
                                                              ))
        elif html == "yes":
            wresult = "<p font-family: Arial> {0:<23}\t{1:<50})\n <br> {2:<23}\t{3:<50} \n</p>\n".format(
                                                            wresult[0][5:-5],
                                                            wresult[1][23:-7],
                                                            wresult[3][6:-5],
                                                            wresult[4][23:-5]
                                                              )
            return wresult
    except:
        printColor("Error occured in cut_file_java7()!")
        traceback.print_exc()
def cut_file_java71(filename,html="no"):
    """
    Edit downloaded content, gain Java 71 values from it by using linux commands
    """
    wresult = []
    try:
#Call linux commands to edit downloaded webpage, cut Java 71 related stuff
        p1 = subprocess.Popen(['cat',filename],stdout=subprocess.PIPE,shell=False)
        p2 = subprocess.Popen(['grep','-n','IBM SDK for z/OS, Java Technology Edition, Version 7 Release 1'],stdin=p1.stdout,stdout=subprocess.PIPE,shell=False)
        p3 = subprocess.Popen(['cut','-d',''':''','-f1' ],stdin=p2.stdout,stdout=subprocess.PIPE,shell=False)
        p4 = subprocess.Popen(['tail','-n','1'],stdin=p3.stdout,stdout=subprocess.PIPE,shell=False)
        woutp4, werrp4 = p4.communicate()
        woutp4 = woutp4.decode('utf-8')
        wstring1 = woutp4.strip() + ",+40p"
        p5 = subprocess.Popen(['sed','-n','-e',wstring1,filename],stdout=subprocess.PIPE,shell=False)
        p6 = subprocess.Popen(['grep','<td>'],stdin=p5.stdout,stdout=subprocess.PIPE,shell=False)
        woutp6, werrp6 = p6.communicate()
        wresult = woutp6.decode('utf-8').split("\r")
        if html == "no":
            print("{0:<23}\t{1:<50}\n{2:<23}\t{3:<50}".format(
                                                            wresult[0][5:-5],
                                                            wresult[1][23:-5].replace(' /','/'),
                                                            wresult[3][6:-5],
                                                            wresult[4][23:-5].replace(' /','/')
                                                             ))
        if html == "yes":
            wresult = "<p font-family: Arial> {0:<23}\t{1:<50}\n <br> {2:<23}\t{3:<50} \n</p>\n".format(
                                                            wresult[0][5:-5],
                                                            wresult[1][23:-5].replace(' /','/'),
                                                            wresult[3][6:-5],
                                                            wresult[4][23:-5].replace(' /','/')
                                                            )
            return wresult
    except:
        printColor("Error occured in cut_file_java71()!")
        traceback.print_exc()
def header(html="no"):
        if html == "no":
            print("\x1b[6;30;42m {0:<73} \x1b[0m".format(
                                                    "Java Standard Edition products on z/OS latest fixpacks"
                                                        ))
            print("{0:-<73}".format("-"))
        elif html == "yes":
            wresult = "<div style='background-color:#33cc33'>\n\t<font color=#661a00> {0:<73} </font>\n</div>\n".format(
                                                                   "Java Standard Edition products on z/OS latest fixpacks"
                                                                   )
            wresult += "<br><hr><br>"
            return wresult
def getArguments():
    try:
#Getting arguments by using getopt
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['html'])
    except getopt.error:
        print("Wrong parameter!")
        print("Usage: \n\t python3 javaptf.py \n\t or \n\t python3 javaptf.py --html")
        sys.exit(1)
    for i, j  in opts:
        if i in ('-h', '--html'):
            main(html="yes")
    else:
        main()
def main(html="no"):
    global wfile
    try:
         wfile = tempfile.NamedTemporaryFile(mode='w+')
         wfile.write(download(wurl))
         if html == "no":
            header()
            cut_file_java8(wfile.name)
            cut_file_java71(wfile.name)
            cut_file_java7(wfile.name)
         elif html == "yes":
            wresult = header(html="yes")
            wresult += cut_file_java8(wfile.name,html="yes")
            wresult += cut_file_java71(wfile.name,html="yes")
            wresult += cut_file_java7(wfile.name,html="yes")
            return wresult
    except:
        printColor("Error occured creating in main()")
        traceback.print_exc()
    wfile.close()
if __name__ == "__main__":
    getArguments()
