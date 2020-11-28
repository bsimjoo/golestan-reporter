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
from logger import Logger

T = 'GR'
class GolestanReporter(threading.Thread):
    def __init__(self, env:lmdb.Environment, users_db, config: configparser.SectionProxy, logger:Logger):
        super.__init__()
        self.cfg = config
        self.env = env
        self.usersDB = users_db
        self.l = logger
        self.last_news = None
        last_news_file_dir = self.cfg.get('last_news_file', 'last news.dat')
        with open(last_news_file_dir, 'rb') as lnfile:
            self.last_news = pickle.load(lnfile)
        self.check_thread:threading.Timer = None

    def get_user_data(self, user, key = None):
        self.l.d(f'getting user({user}) info',T)
        try:
            with self.env.begin(self.usersDB) as txn:
                data = txn.get(user.enconde())
            user_info = pickle.loads(data)
            if key:
                return user_info[key]
            return user_info
        except Exception as e:
            self.l.e('error on getting user info',T)
            self.l.d(f'{type(e)}: {e}',T)

    def check_and_mail(self, timer=0):
        n = self.get_last_news()
        if n is not None and n != self.last_news:
            # TADA! new news!
            self.l.i('new news. prepairing to send emails...')
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
                        info = pickle.loads(info)
                        if info.email != '' and not info['golestan_reporter.mute']:
                            self.l.d(f"sending mail to user({info['uni_code']}): {info['email']}", T)
                            msg['To'] = info['email']
                            server.sendmail(
                                self.cfg['sender_email'], msg['To'], msg.as_string())
            except Exception as e:
                self.l.e('cannot do check & mail',T)
                self.l.d(f'{type(e)}: {e}, n: {n}',T)
            finally:
                server.quit()
        self.check_thread = threading.Timer(
            timer, self.check_and_mail, (timer,))

    def run(self):
        self.check_and_mail(self.cfg.getint('check_interval', 100))

    def stop(self):
        self.l.i('thread is stoping...',T)
        try:
            self.check_thread.join()
            self.check_thread.cancel()
        except:
            pass
