import logging
from utils.logger import Logger
def init_global(file_log="logger.log"):  # initialization of all global variables
    '''
    this function creates all global objects that have to be shared among all classes
    '''
    global logger
    logger_class = Logger(file_log)
    logger=logger_class.log
