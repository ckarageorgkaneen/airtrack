import logging

from airtrack.settings import AIRTRACK_DEBUG_PREFIX


def create_logger(name):
    logger = logging.getLogger(name)
    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # Create formatter
    formatter = logging.Formatter(
        f'%(levelname)s:%(name)s:{AIRTRACK_DEBUG_PREFIX}%(message)s')
    # Add formatter to ch
    ch.setFormatter(formatter)
    # Add ch to logger
    logger.addHandler(ch)
    logger.propagate = False
    return logger
