import logging
import os
import platform
from utils.check_updates import VERSION_CURRENT

LOGGING_APP  = 'Kozmadeus'
LOGGING_FILE = 'kozmadeus.log'
SEPARATOR = ('---------------------------------'
             '---------------------------------'
             '--------------')

def InitRootLogger():
    logger = logging.getLogger(LOGGING_APP)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOGGING_FILE, mode='w+')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fh_formatter = logging.Formatter('[%(asctime)s][%(module)s][%(levelname)s]: %(message)s', '%H:%M:%S')
    ch_formatter = logging.Formatter('[%(levelname)s]: %(message)s', '%H:%M:%S')
    fh.setFormatter(fh_formatter)
    ch.setFormatter(ch_formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)


def _PlatformLogs(logger):
    logger.debug(f'Kozmadeus version: "{VERSION_CURRENT}"')
    log_file_path = os.path.realpath(LOGGING_FILE)
    logger.debug(f'Logging to: "{log_file_path}"')
    system_info = str((platform.platform(), platform.machine(),
                       platform.processor()))
    logger.debug(f'System Info: {system_info}')
    logger.debug(f'Python version: {platform.python_version()}')


def GetLogger():
    logger = logging.getLogger(f'{LOGGING_APP}.main')
    _PlatformLogs(logger)
    logger.debug(SEPARATOR)
    return logger
