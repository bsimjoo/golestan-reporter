import configparser
import lmdb
from logger import Logger

# main.py will run golestan_reporter and any other services
from golestan_reporter import GolestanReporter

CONFIG_FILE_DIR = 'config.ini'
CONFIG_FILE_ENCODER = 'utf8'
DEBUG = True

cfg = configparser.ConfigParser()
# TODO: use a dynamic cfg directory given in arg
with open(CONFIG_FILE_DIR, encoding=CONFIG_FILE_ENCODER) as cfgFile:
    cfg.readfp(cfgFile)
maincfg=cfg['Main']
logger = Logger(maincfg.get('log_dir','.log'), maincfg.getint('log_level',0), DEBUG)
with lmdb.open(maincfg.get('db_dir','.db'), max_dbs=2) as env:
    usersDB = env.open_db(maincfg.get('users_database','users').enconde())
    golestan_reporter = GolestanReporter(users_db=usersDB, config=cfg['Golestan reporter'])

golestan_reporter.start()

# TODO: run web tools