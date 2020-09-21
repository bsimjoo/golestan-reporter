import re,cherrypy,lmdb,threading
import smtplib,ssl,string,random
from os import path
from config import *
from mailconfig import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def ConvertTemplateCode(TemplateName:str,VarsDictionary={},LoopSource=None):
    template_file_path = path.join(TEMPLATES_DIR,TEMPLATES_DICTIONARY[TemplateName])
    VarsDictionary+=TEMPLATE_VALUES_DICTIONARY
    with open(template_file_path) as template_file:
        result=template_file.read()
    searchPattern=re.compile(r'(\[::([^\]]*)])')        #searching for template code variables
    for oldString,variableName in searchPattern.findall(result):
        if variableName in VarsDictionary:
            result=result.replace(oldString,VarsDictionary[variableName])
    if LoopSource!=None:

        for regGroups in re.findall(r'(\[::foreach (\w*)](\n(\s*((?!\[::end\]).)*\n?)*)\[::end])',result):
            #searching for template code foreach
            #foreach regex groups:
            # 0: old full string for replacing
            # 1: foreach source
            # 2: repeatable template
            # 3: the last content line.(no needed, just needed for regex algurithm)
            newHtml=''
            for localVarsDict in LoopSource[regGroups[1]]:
                sec=ConvertTemplateCode(regGroups[2])
                sec=ConvertTemplateCode(sec,localVarsDict)
                newHtml+=sec
            result=result.replace(regGroups[0],newHtml)
    return result

class mail_sender:
    def __init__(self):
        self.context = ssl.create_default_context()
        self.server=None
    
    def connect(self):
        self.server = smtplib.SMTP(SMTP_SERVER,SMTP_PORT_SSL)
        self.server.ehlo() # Can be omitted
        self.server.starttls(context=self.context) # Secure the connection
        self.server.ehlo() # Can be omitted
        self.server.login(SENDER_EMAIL, PASSWORD)
    
    def send(self,to,msg:MIMEMultipart):
        msg['To'] = to
        self.server.sendmail(SENDER_EMAIL, to, msg.as_string())

    def close(self):
        self.server.quit()

class root:
    def __init__(self,env,db):
        self.env=env
        self.db=env.open_db(db)
        self.keys=[]
        self.mail_keys={}

    def get_random_string(self,length):
        letters = string.ascii_lowercase+string.digits+string.ascii_uppercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    def expire_key(self,enum,index):
        del enum[index]

    @cherrypy.expose
    def index(self):
        # generate a temporary key to verify registeration
        key=''
        while key not in self.keys:
            key=self.get_random_string(16)
        self.keys.append(key)
        # expire key after 15 minutes
        threading.Timer(15*60*60,self.expire_key,(self.keys,self.keys.index(key))).start()
        return ConvertTemplateCode('HOME_PAGE',{'key':key})
    
    @cherrypy.expose
    def register(self,key=None,uni_code=None,email=None,**args):
        if key in self.keys:
            # register
            with self.env.begin(self.db) as txn:
                if txn.get(uni_code) == None:
                    # new user. prepairing for registration
                    ms=mail_sender()
                    ms.connect()
                    msg = MIMEMultipart('alternative')
                    msg['From'] = EMAIL_SENDER_NAME
                    msg['Subject'] = REGISTRATION_MAIL_SUBJECT
                    key=''
                    while key not in self.mail_keys:
                        key=self.get_random_string(36)
                    self.mail_keys[key]=email
                    # expire key after 30 minutes
                    threading.Timer(30*60*60,self.expire_key,(self.mail_keys,key)).start()   
                    news_html=ConvertTemplateCode('REGISTRATION_MAIL_BODY',args+{'link':WEB_SERV_ROOT+'verify?q='+key})
                    msg.attach(MIMEText(news_html,'html'))
                    ms.send(email,msg)
            return ConvertTemplateCode('VARIFY_MAIL_SENT',args)
        raise cherrypy.HTTPError(404)

def run_web_serv(env,db):
    conf = {"global":
        {
            "server.socket_host": WEB_SERV_BIND_TO,
            "server.socket_port": WEB_SERV_PORT,
            "log.screen": WEB_SERV_LOG,
            "log.access_file": WEB_SERV_ACCESS_FILE,
            "log.error_file": WEB_SERV_ERROR_FILE,
            "tools.staticdir.root": WEB_SERV_STATIC_ROOT,
            "tools.staticdir.on": WEB_SERV_STATIC_ON,
            "tools.staticdir.dir": WEB_SERV_STATIC_DIR
        }
    }
    cherrypy.tree.mount(root(env,db),'/',conf)
    cherrypy.engine.start()

def stopWebServ():
    cherrypy.server.bus.exit()
    cherrypy.engine.block()