###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 license License       #
# Github: https://github.com/Crowfunder                       #
###############################################################
# Why a custom logger? Simply to prevent circular imports     #
# The whole framework is designed according to one-way        #
# descending imports tree                                     #
# In order to use "logging" module I'd have to                #
# make modules import logging functs somehow                  #
###############################################################

import os
import sys
import platform
import datetime
import traceback

# Constants
SEPARATOR = ('---------------------------------'
             '---------------------------------'
             '--------------')

# May you be blessed, whoever you are that made this thing
# https://stackoverflow.com/questions/616645/how-to-duplicate-sys-stdout-to-a-log-file
class Tee(object):


    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self
        
        # Gotta notify the timestamper (get it?)
        # that there is a newline
        # timestamps are added if a newline is detected
        # as previous data
        self.data_old = '\n'

        # Init logging info
        log_file_path = os.path.realpath(self.file.name)
        self.file.write(f'Logging to: "{log_file_path}" \n')

        # Timestamp 
        x = datetime.datetime.now()
        start_time = x.strftime('%d/%m/%Y')
        self.file.write(f'Date (DD/MM/YYYY): {start_time} \n')

        # System Info
        system_info = str((platform.platform(), platform.machine(), 
                           platform.processor()))
        self.file.write(f'System Info: {system_info} \n')

        # Runtime Info
        self.file.write(f'Python version: {platform.python_version()} \n')
        self.file.write(f'{SEPARATOR}\n')

        self.file.flush()


    def close(self):
        if self.stdout is not None:
            sys.stdout = self.stdout
            self.stdout = None

        if self.file is not None:
            self.file.close()
            self.file = None


    def write(self, data):

        # Detect a newline from a stored previous 
        # data write() input and add a timestamp
        if '\n' in self.data_old:
            self.timestamper()

        self.file.write(data)
        self.stdout.write(data)
        self.flush()
        
        self.data_old = data


    # Flush write buffer
    def flush(self):
        self.file.flush()
        self.stdout.flush()

    # Log exceptions and format them
    # using the timestamper and "traceback" module
    def log_exception(self):
        self.timestamper()
        tb = traceback.format_exc()
        self.file.write(f'[ERROR]: {tb}')


    # Adds a timestamp
    def timestamper(self):
        x = datetime.datetime.now()
        timestamp = x.strftime('%H:%M:%S')
        self.file.write(f'[{timestamp}]')
        self.file.flush()


    def __del__(self):
        self.close()



def LoggerInit():
   logger = Tee('kozmadeus.log', 'w+')
   return logger
