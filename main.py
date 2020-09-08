import requests,re
from bs4 import BeautifulSoup
import threading
import smtplib,ssl
import signal
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib,os
# common configurations
from config import *
# configuration of my mail account:
from mailconfig import *
# This file has been removed from git. Please create a new file (mailconfig.py) like the one below:
# sender_email = 'yourname@example.com'
# password = r'yourpassword'

def get_news():
    req = requests.get(golestan_news_source)
    soup = BeautifulSoup(req.content,'html.parser')
    news = soup.find('div',class_='newsitm')
    newsDict = {}
    news_title = news('span','newsitmtitle')[1].b.get_text()
    newsDict['title'] = str(news_title)
    news_dateText = str(news.find('span','newsitmpubdate').get_text())
    pat = r'\d+/\d+/\d+'
    date = re.findall(pat,news_dateText)[0]
    newsDict['date'] = date
    news_body = news.find('div','newsitmbody').div.p
    newsDict['body'] = str(news_body)
    return newsDict

checkThread = None
newsHash = None
if os.path.isfile(last_news_hash_file):
    with open(last_news_hash_file) as lnfile:
        try:
            newsHash=lnfile.read()
        except Exception as e:
            print('unable to read latest news file', type(e), e, sep = '\n')

locker=threading.RLock()
def checkAndMail(timer = 0):
    n = None
    try:
        n = get_news()
    except Exception as e:
        print('Error while getting news', type(e), e, sep = '\n')
    else:
        global newsHash
        newsString = '\n'.join(n.values())
        result = hashlib.md5(newsString.encode()).hexdigest()
        if result != newsHash:
            print('new notification. preparing to send mails')
            newsHash = result
            # save latest news hash in local file
            with open(last_news_hash_file, 'w') as lnfile:
                try:
                    lnfile.write(newsHash)
                except Exception as e:
                    print('unable to write last news hash file', type(e), e, sep='\n')
                    return
            #send mails
            context = ssl.create_default_context()
            # Try to log in to server and send email
            try:
                server = smtplib.SMTP(smtp_server,port)
                server.ehlo() # Can be omitted
                server.starttls(context=context) # Secure the connection
                server.ehlo() # Can be omitted
                server.login(sender_email, password)
                msg = MIMEMultipart('alternative')
                msg['From'] = from_
                msg['Subject']=n['title']
                msg.attach(MIMEText(n['body'],'html'))
                with locker:
                    with open(mail_list_file) as mailList:
                        for mailAdd in mailList:
                            print('sending mail to:', mailAdd)
                            msg['To'] = mailAdd
                            server.sendmail(sender_email, mailAdd, msg.as_string())
            except Exception as e:
                # Print any error messages to stdout
                print(e)
            finally:
                server.quit()

    if timer>0:
        global checkThread
        checkThread = threading.Timer(timer, checkAndMail, [timer])
        checkThread.start()

mainLoop=True
mainThread=threading.currentThread()
def keyboardInterruptHandler(signal, frame):
    print(f"KeyboardInterrupt (ID: {signal}) has been caught. Cleaning up...")
    try:
        global mainLoop
        mainLoop=False
        checkThread.cancel()
        checkThread.join()
        print('bye bye!')
        exit(0)
    except:
        pass

if __name__ == "__main__":
    signal.signal(signal.SIGINT, keyboardInterruptHandler)
    print('press ctrl+c to exit')
    # checking and mailing every 5 minutes
    checkAndMail(5*60)
    while mainLoop:
        try:
            mail=input('Enter mail address to add: ')
        except EOFError:
            # when ctrl+c pressed
            pass
        with locker:
            with open(mail_list_file,'a') as mailList:
                mailList.write(mail)