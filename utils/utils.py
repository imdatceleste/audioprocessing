# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
import logging
"""
split_voice utils

Created: 2017-12-20 ??:?? CET, KA
"""
logger = logging.getLogger(os.path.basename(sys.argv[0]))

def convertMilliseconsTime(mili=0):
    """
    Converts miliseconds to 'hh:mm:ss' format
    """    
    seconds=(mili/1000)%60
    seconds = int(seconds)
    minutes=(mili/(1000*60))%60
    minutes = int(minutes)
    hours=(mili/(1000*60*60))%24
    return ("%002d:%002d:%002d" % (hours, minutes, seconds))


# Color the command line with the color options below
def make_colored(colorCode):
    def make_bold(text, bold=False):
        code = colorCode
        if bold:
            code = '1;%s' % code
        return '\033[%sm%s\033[0m' % (code, text)
    return make_bold

red = make_colored('31')
# green = make_colored('32')
# yellow = make_colored('33')
# blue = make_colored('34')
# magenta = make_colored('35')
# cyan = make_colored('36')
# white = make_colored('37')


def configure_logger(logFileName=None):
    """
    Setup logging. This configures either a console handler, a file handler, or both and adds them to the root logger.
    Params:
        file_log (str): full filepath for file logger output
    """
    if logFileName is None:
        raise ValueError("Log file name could not be found!")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-7s (%(name)s) %(message)s')
    if not logger.handlers:
        # Create a file handler
        fileHandler = logging.FileHandler(logFileName, mode='w')
        fileHandler.setLevel(logging.INFO)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        # Create a console handler
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.ERROR)
        consoleHandler.setFormatter(formatter)
        logger.addHandler(consoleHandler)
