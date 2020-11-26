import requests
import configparser
import cherrypy
import re
import lmdb
import pickle
import smtplib
import ssl
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from User import User


class GolestanReporter(threading.Thread):
    def __init__(self, users_db: lmdb.Environment, config: configparser.SectionProxy):
        super.__init__()
        self.cfg = config
        self.usersDB = users_db
        self.last_news = None
        last_news_file_dir = self.cfg.get('last_news_file', 'last news.dat')
        with open(last_news_file_dir, 'rb') as lnfile:
            self.last_news = pickle.load(lnfile)
        self.check_thread:threading.Timer = None

    def get_user_data(self, user=None) -> User:
        with self.usersDB.begin() as txn:
            data = txn.get(user.enconde())
        user_info = pickle.loads(data)
        return user_info

    def set_user_data(self, user, value, key=None):
        if key:
            value_ = value
            value = self.get_user_data(user)
            value[key] = value_
        data = pickle.dumps(value)
        with self.usersDB.begin(write=True) as txn:
            txn.put(key.enconde(), data)

    def get_last_news(self):
        req = requests.get(self.cfg["news_source"])
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
                    server = smtplib.SMTP(
                        self.cfg['smtp_server'], int(self.cfg['smtp_port']))
                    server.ehlo()  # Can be omitted
                    server.starttls(context=context)  # Secure the connection
                    server.ehlo()  # Can be omitted
                    server.login(
                        self.cfg['sender_email'], self.cfg['email_password'])
                    msg = MIMEMultipart('alternative')
                    msg['From'] = self.cfg.get(
                        'sender_name', 'Golestan reporter')
                    msg['Subject'] = n['title']
                    msg.attach(MIMEText(n['body'], 'html'))
                    with self.usersDB.begin() as txn:
                        for user, info in txn.cursor:
                            info: User = pickle.loads(info)
                            if info.email != '' and not info.other_properties['golestan_reporter.mute']:
                                print('sending mail to:',
                                      info.uni_code, info.email)
                                msg['To'] = info.email
                                server.sendmail(
                                    self.cfg['sender_email'], msg['To'], msg.as_string())
                except Exception as e:
                    # Print any error messages to stdout
                    print(e)
                finally:
                    server.quit()
        self.check_thread = threading.Timer(
            timer, self.check_and_mail, (timer,))

    def run(self):
        self.check_and_mail(self.cfg.getint('check_interval', 100))

    def stop(self):
        try:
            self.check_thread.join()
            self.check_thread.cancel()
        except:
            pass


class GolestanReporterWeb:
    def __init__(self, users_db: lmdb.Environment, config: configparser.SectionProxy):
        self.cfg = config
        self.usersDB = users_db
