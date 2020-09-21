from sys import stdout

GOLESTAN_NEWS_SOURCE='http://golestan.hormozgan.ac.ir/FORMS/F0284_PROCESS_NEWS/news.aspx'
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT_SSL = 587 # For starttls
DATABASE_PATH='db.lmdb'
EMAIL_SENDER_NAME='سامانه اطلاع رسانی گلستان'
REGISTRATION_MAIL_SUBJECT='تایید هویت برای ثبت نام در سامانه اطلاع رسانی گلستان'
LAST_NEWS_HASH='last_news.md5'
LOG_MAIL_SEND=True
LOG_MAIL_SEND_TO=stdout
WEB_SERV_BIND_TO='0.0.0.0'
WEB_SERV_PORT='8080'
WEB_SERV_ACCESS_FILE='access'
WEB_SERV_ERROR_FILE='error'
WEB_SERV_LOG=True
WEB_SERV_STATIC_ON=False
WEB_SERV_STATIC_ROOT='F:/Projects/Python/golestan reporter/templates/'
WEB_SERV_STATIC_DIR=''
WEB_SERV_ROOT='http://localhost:8088/'
TEMPLATES_DIR='templates'
TEMPLATES_DICTIONARY = {
    'HOME_PAGE':'home_page.html',
    'MAIL_BODY':'mail.html',
    'REGISTRATION_MAIL_BODY':'register_mail.html',
    'VERIFY_MAIL_SEND':'register_mail_sent.html'
}
TEMPLATE_VALUES_DICTIONARY={

}