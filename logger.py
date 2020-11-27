import os
from datetime import datetime as time

class Logger:
    def __init__(self, destination, log_level=0, debug=False):
        # log levels:
        # 0 nothing
        # 1 error
        # 2 warning
        # 3 info
        # 4 debug
        assert 0<=log_level<=4, 'log level is not in range'
        self.debug = debug
        self.log_level = log_level
        self.last_lines_count = last_lines_count
        self.__write_log = lambda x: print(x)
        if destination:
            self.__write_log = lambda x: self.__write_to_file(destination,x)

        
    def __write_to_file(self, file, log):
        with open(file,'a+') as logfile:
            logfile.seef(0)
            data = logfile.read(100)
            if len(data) > 0:
                logfile.write(os.linesep)
            logfile.write(log)

    def log(self, level, message, tag=None):
        # What is tag?
        # tag is useful for programmers to trace errors and infos in code
        # tags can be a location in codes like filenumber+line and it can help
        # while debuging
        if tag:
            self.__write_log(f'[{time.now().strftime("%Y%m%d%H%M")}][{level}][{tag}]: {message}')
        else:
            self.__write_log(f'[{time.now().strftime("%Y%m%d%H%M")}][{level}]: {message}')

    def d(self, log, tag=None):
        'debug log level'
        if self.debug and self.log_level>=4:
            self.log('debug',log,tag)

    def i(self, log, tag=None):
        'information log level'
        if self.log_level>=3:
            self.log('info',log,tag)
        
    def w(self, log, tag=None):
        'warning log level'
        if self.log_level>=2:
            self.log('warning',log,tag)

    def e(self, log, tag=None):
        'error log level'
        if self.log_level>=1:
            self.log('error',log,tag)
        

