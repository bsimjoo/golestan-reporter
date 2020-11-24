import requests
import configparser
import re
import lmdb
import pickle
import smtplib,ssl
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from User import User


class GolestanReporter:
    def __init__(self):
        self.cfg = configparser.ConfigParser()
        # TODO: use a dynamic cfg directory given in arg
        self.cfg.read('cfg.ini')
        self.defcfg = self.cfg['default']
        self.internalDB = None
        self.usersDB = None
        with lmdb.open(self.defcfg.get('db path','./'), max_dbs=2) as env:
            self.usersDB = env.open_db(self.defcfg.get('users database','users').enconde())
        self.last_news = None
        last_news_file_dir = self.defcfg.get('last news file','last news.dat')
        with open(last_news_file_dir, 'rb') as lnfile:
            self.last_news = pickle.load(lnfile)
        self.check_thread = None

    def get_user_data(self, user, property=None):
        with self.usersDB.begin() as txn:
            data = txn.get(user.enconde())
        user_info = pickle.load(data)
        if property:
            return user_info[property]
        else:
            return user_info

    def set_user_data(self, user, value, key=None):
        if key:
            value_ = value
            value = self.get_user_data(user)
            value[key] = value_
        data = pickle.dump(value)
        with self.usersDB.begin(write=True) as txn:
            txn.put(key.enconde(), data)

    def get_last_news(self):
        req = requests.get(self.defcfg["news source"])
        soup = BeautifulSoup(req.content, 'html.parser')
        news = soup.find('div', class_='newsitm')
        newsDict = {}
        news_title = news('span', 'newsitmtitle')[1].b.get_text()
        newsDict['title'] = str(news_title)
        news_dateText = str(news.find('span', 'newsitmpubdate').get_text())
        pat = r'\d+/\d+/\d+'
        date = re.findall(pat, news_dateText)[0]
        newsDict['date'] = date
        news_body = news.find('div', 'newsitmbody').div.p
        newsDict['body'] = str(news_body)
        return newsDict

    def check_and_mail(self, timer=0):
        n = None
        try:
            n = self.get_last_news()
        except Exception as e:
            print('Error while getting news', type(e), e, sep='\n')
            # TODO: a better log
        else:
            if n != self.last_news:
                # TADA! new news!
                print('preparing to send notifications')
                context = ssl.create_default_context()
                # Try to log in to server and send email
                try:
                    server = smtplib.SMTP(self.defcfg['smtp server'], int(self.defcfg['smtp port']))
                    server.ehlo() # Can be omitted
                    server.starttls(context=context) # Secure the connection
                    server.ehlo() # Can be omitted
                    server.login(self.defcfg['sender email'], self.defcfg['email password'])
                    msg = MIMEMultipart('alternative')
                    msg['From'] = self.defcfg['from']
                    msg['Subject']=n['title']
                    msg.attach(MIMEText(n['body'],'html'))
                    with self.usersDB.begin() as txn:
                        for user, info in txn.cursor:
                            info:User = pickle.load(info)
                            if info.email !='' and not info.other_properties['golestan reporter mute']:
                                print('sending mail to:', info.uni_code, info.email)
                                msg['To'] = info.email
                                server.sendmail(self.defcfg['sender email'], msg['To'], msg.as_string())
                except Exception as e:
                    # Print any error messages to stdout
                    print(e)
                finally:
                    server.quit()
        self.check_thread = threading.Timer(timer, self.check_and_mail,(timer,))
