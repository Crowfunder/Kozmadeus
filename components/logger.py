###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

import logging
import os
import platform
from components.check_updates import VERSION_CURRENT


LOGGING_APP  = 'Kozmadeus'
LOGGING_FILE = 'kozmadeus.log'
SEPARATOR = ('---------------------------------'
             '---------------------------------'
             '--------------')


def InitRootLogger():
    logger = logging.getLogger(LOGGING_APP)

    # Failsafe in case InitRootLogger was already ran once.
    if len(logger.handlers) > 0:
        return
    logger.setLevel(logging.DEBUG)

    # Logfile handler
    fh = logging.FileHandler(LOGGING_FILE, mode='w+')
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter('[%(asctime)s][%(module)s][%(levelname)s]: %(message)s', '%H:%M:%S')
    fh.setFormatter(fh_formatter)

    # Stdout handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter('[%(levelname)s]: %(message)s', '%H:%M:%S')
    ch.setFormatter(ch_formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
    _PlatformLogs(logger)


def _PlatformLogs(logger):
    logger.debug(f'Kozmadeus version: "{VERSION_CURRENT}"')
    log_file_path = os.path.realpath(LOGGING_FILE)
    logger.debug(f'Logging to: "{log_file_path}"')
    system_info = str((platform.platform(), platform.machine(),
                       platform.processor()))
    logger.debug(f'System Info: {system_info}')
    logger.debug(f'Python version: {platform.python_version()}')
    logger.debug(SEPARATOR)


def GetLogger():
    '''
    Returns the logger object.
    '''
    logger = logging.getLogger(LOGGING_APP)
    return logger


def EndLogging():
    '''
    Display logging end flairs.
    '''
    logger = logging.getLogger(LOGGING_APP)
    logger.info('Finished logging to "%s"', LOGGING_FILE)
    logger.info(SEPARATOR)
