import requests,re,hashlib,os,lmdb,json
import threading,signal
from bs4 import BeautifulSoup
from os import path
from web_tools import *

# common configurations
from config import *
# configuration of my mail account:
from mailconfig import *
# This file has been removed from git. Please create a new file (mailconfig.py) like the one below:
# sender_email = 'yourname@example.com'
# password = r'yourpassword'

def get_news():
    req = requests.get(GOLESTAN_NEWS_SOURCE)
    soup = BeautifulSoup(req.content,'html.parser')
    news = soup.find('div',class_='newsitm')
    news_info = {}
    news_title = news('span','newsitmtitle')[1].b.get_text()
    news_info['title'] = str(news_title)
    news_dateText = str(news.find('span','newsitmpubdate').get_text())
    pat = r'\d+/\d+/\d+'
    date = re.findall(pat,news_dateText)[0]
    news_info['date'] = date
    news_body = news.find('div','newsitmbody').div.p
    news_info['body'] = str(news_body)
    news_info['link'] = str(news_body.a['href'])
    return news_info

check_thread = None
last_hash = None
if os.path.isfile(LAST_NEWS_HASH):
    with open(LAST_NEWS_HASH) as lnfile:
        try:
            last_hash = lnfile.read()
        except Exception as e:
            print('unable to read latest news hash file', type(e), e, sep = '\n')

jencode = lambda x: json.JSONEncoder().encode(x.decode()).encode()
jdecode = lambda x: json.JSONDecoder().decode(x.decode())
env = lmdb.open(DATABASE_PATH,max_dbs=2)
users_db=env.open_db(b'users')

def check_and_mail(timer=0):
    n=get_news()
    news_hash = '\n'.join(n.values())
    news_hash = hashlib.md5(news_hash.encode()).hexdigest()
    global last_hash
    if last_hash!=news_hash:
        # new news!
        last_hash = news_hash
        with open(LAST_NEWS_HASH, 'w') as lnfile:
            try:
                lnfile.write(news_hash)
            except Exception as e:
                print('unable to write last news hash file', type(e), e, sep='\n')
                return

    with env.begin(users_db) as txn:
        ms = mail_sender()
        ms.connect()
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_SENDER_NAME
        msg['Subject']=n['title']
        news_html=ConvertTemplateCode('MAIL_BODY',n)
        msg.attach(MIMEText(news_html,'html'))
        for uni_code,info in txn.cursor():
            info=jdecode(info)
            email=info['email']
            if LOG_MAIL_SEND:
                print(f'sending email for student {uni_code} to {email}',file=LOG_MAIL_SEND_TO)
            ms.send(email,msg)
        ms.close()

    if timer>0:
        check_thread=threading.Timer(timer,check_and_mail,(timer,))
        check_thread.start()
    