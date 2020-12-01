import logging

class Logger:

    log = None
    fh=None
    formatter=None

    def __init__(self):
        self.log = logging.getLogger('LOGGER')
        self.fh = logging.FileHandler('logger.log')
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def set_level(self, level=logging.DEBUG):
        self.log.setLevel(level)
        self.fh.setLevel(level)
        self.fh.setFormatter(self.formatter)
        self.log.addHandler(self.fh)