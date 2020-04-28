import colorlog, logging

loggers = []
level = logging.INFO

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s[%(asctime)s][%(levelname)s][%(name)s]: %(message)s', datefmt="%d/%m/%Y %H:%M:%S"))

def setup():
    #log = logging.getLogger('werkzeug')
    #log.setLevel(logging.DEBUG)
    #log.addHandler(handler)
    pass

def setLevel(l):
    level = l
    for logger in loggers:
        logger.setLevel(level)

def get(name):
    logger = colorlog.getLogger(name.upper())
    logger.addHandler(handler)
    logger.setLevel(level)
    loggers.append(logger)

    return logger

def register(logger):
    logger.addHandler(handler)
    logger.setLevel(level)
    loggers.append(loggers)

def remove(logger):
    loggers.remove(logger)