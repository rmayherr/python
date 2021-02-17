import smtplib, traceback, datetime
import javaptf as j

port = 25
smtp_server = "????.com"
mail_from = "????.com"
mail_to = "?????.ibm.com"
subject = "ShopZ latest java packages"

def send(msg=""):
    content= ""
    srv = smtplib.SMTP(smtp_server,port)
    headers = {
                'Content-Type': 'text/html; charset=utf-8',
                'Content-Disposition': 'inline',
                'Content-Transfer-Encoding': '8bit',
                'From': mail_from,
                'To': mail_to,
                'Date': datetime.datetime.now().strftime('%a, %d %b %Y  %H:%M:%S %Z'),
                'X-Mailer': 'python',
                'Subject': subject
            }
    for key,value in headers.items():
        content += "%s:%s\n" % (key,value)
    content += "\n%s\n" %(msg)
    try:
        srv.connect()
        srv.sendmail(headers['From'],headers['To'],content.encode('utf-8'))
        srv.quit()
    except:
        traceback.print_exc()
try:
    send(msg=j.main(html="yes"))
except:
    traceback.print_exc()
#source https://petermolnar.net/not-mime-email-python-3/
