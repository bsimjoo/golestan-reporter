import configparser
import lmdb
import cherrypy
import pickle
from hashlib import sha256
from logger import Logger

# main.py will run golestan_reporter and any other services
from golestan_reporter import GolestanReporter

T = 'main'
CONFIG_FILE_DIR = 'config.ini'
CONFIG_FILE_ENCODER = 'utf8'
DEBUG = True
DEV_PASS = 'eda57e1df3f6fb8a9ac094b95fc9cfb20d4783db8ecc8261f232f606fe35cbe3'       # hint: adamsmozi

@cherrypy.tools.register('before_handler')
def auth(class_):
    s = cherrypy.session
    if s.get('user class') in class_:
        return
    else:
        raise cherrypy.HTTPRedirect('/signin')

class Root:
    def __init__(self, env, users_db, config: configparser.SectionProxy, logger: Logger):
        self.env = env
        self.usersDB = users_db
        self.cfg = config
        self.l = logger
        self.get_hashsum = lambda x: sha256(x.encode()).hexdigest()

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

    def set_user_data(self, user, value, key=None):
        self.l.i(f'setting user({user}) info',T)
        self.l.d(f'key:{key}'+', value:{value}'if key else ', value is full user info',T)
        try:
            if key:
                value_ = value
                value = self.get_user_data(user)
                value[key] = value_
            data = pickle.dumps(value)
            with self.env.begin(self.usersDB,write=True) as txn:
                txn.put(key.enconde(), data)
        except Exception as e:
            self.l.e('error on setting user info',T)
            self.l.d(f'{type(e)}: {e}',T)

    @cherrypy.expose
    def signup(self, **info):
        pass

    @cherrypy.expose
    def verify(self, q):
        pass

    @cherrypy.expose
    def signin(self, username=None, password=None):
        if username is None or password is None:
            # signin form
            pass
        else:
            # do signin:
            if username == 'admin':
                if self.get_hashsum(password)==self.cfg['admin_pass_sha256']:
                    cherrypy.session['user class']='admin'
                    raise cherrypy.HTTPRedirect('/admincp')
                else:
                    return 'incorrect password'
            elif username == 'developer' and DEBUG:
                if self.get_hashsum(password)==DEV_PASS:
                    cherrypy.session['user class']='dev'
                    raise cherrypy.HTTPRedirect('/devtool')
                    # TODO: add devtool
                else:
                    return 'incorrect password'
            else:
                user_info = self.get_user_data(username)
                if user_info:
                    if self.get_hashsum(password) == user_info['passhash']:
                        cherrypy.session['user class'] = 'user'
                        cherrypy.session['user'] = username
                        raise cherrypy.HTTPRedirect('/cp')
                    else:
                        return 'incorrect password'
                else:
                    return 'incorrect username'

    @cherrypy.expose
    def index(self):
        # no index page at now. this will redirect user to signin
        s = cherrypy.session
        if s.get('user class') == 'admin':
            raise cherrypy.HTTPRedirect('/admincp')
        elif s.get('user class') == 'user':
            raise cherrypy.HTTPRedirect('/cp')
        else:
            raise cherrypy.HTTPRedirect('/signin')

    @cherrypy.auth(('dev','users'))
    def cp(self):
        s = cherrypy.session
        student = None
        if s.get('user class') == 'user':
            if s.get('user') != None:
                student = self.get_user_data(s.get('user'))
            else:
                self.l.w('user class is user but no user attribute found in session',T)
                raise cherrypy.HTTPRedirect('/signin')
        # TODO: add web interface

    @cherrypy.auth(('dev','admin'))
    def admincp(self):
        # TODO: add web interface
        pass


cfg = configparser.ConfigParser()
# TODO: use a dynamic cfg directory given in arg
with open(CONFIG_FILE_DIR, encoding=CONFIG_FILE_ENCODER) as cfgFile:
    cfg.readfp(cfgFile)
maincfg=cfg['Main']
logger = Logger(maincfg.get('log_dir','.log'), maincfg.getint('log_level',0), DEBUG)
with lmdb.open(maincfg.get('db_dir','.db'), max_dbs=2) as env:
    usersDB = env.open_db(maincfg.get('users_database','users').encode())
    golestan_reporter = GolestanReporter(users_db=usersDB, config=cfg['Golestan reporter'])

golestan_reporter.start()

# TODO: run web tools