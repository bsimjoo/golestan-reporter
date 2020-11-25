import os
from datetime import datetime as time

class Logger:
    # admin could see last n lines of log, so LimitedLogQueue designed to save last lines of log
    class LimitedLogQueue:
        class Node:
            def __init__(self, value, next=None):
                self.next = next
                self.value = value

        def __init__(self, size: int):
            self.size = size
            self.__head = self.__tail = None
            self.__len = 0

        def add(self, value):
            node = Node(value)
            if self.__tail:
                self.__tail = self.__tail.next = node
            else:
                self.__head = self.__tail = node
            
            if self.__len > self.size:
                self.__head = self.__head.next

        def __iter__(self):
            t = self.__head
            while t.next:
                yield t
                t = t.next
        
        def __repr__(self):
            for n in self:
                print(n.value)

    def __init__(self, destination, last_lines_count=50, debug=False):
        self.debug = debug
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
        self.__write_log(f'[{time.now().strftime("%Y%m%d%H%M")}][{level}][{tag}]: {message}')

    def d(self, log, tag=None):
        'debug log level'
        if self.debug:
            self.log('debug',log,tag)

    def i(self, log, tag=None):
        'information log level'
        self.log('info',log,tag)
        
    def w(self, log, tag=None):
        'warning log level'
        self.log('warning',log,tag)

    def e(self, log, tag=None):
        'error log level'
        self.log('error',log,tag)
        

