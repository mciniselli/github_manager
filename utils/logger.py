import logging
import os

class Logger:

    log = None
    fh=None
    formatter=None

    def __init__(self, name="logger.log"):
        self.log = logging.getLogger('LOGGER')
        self.fh = logging.FileHandler(os.path.join(os.getcwd(), name))
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.formatter_console = logging.Formatter('%(message)s')

        # create console handler with a higher log level
        self.ch = logging.StreamHandler()
        self.set_level()

    def set_level(self, level=logging.DEBUG):
        self.log.setLevel(level)
        self.fh.setLevel(level)
        self.ch.setLevel(level)

        self.fh.setFormatter(self.formatter)
        self.ch.setFormatter(self.formatter_console)

        if len(self.log.handlers)==0:
            self.log.addHandler(self.fh)
            self.log.addHandler(self.ch)

