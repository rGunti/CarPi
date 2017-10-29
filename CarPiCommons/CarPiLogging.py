#!/usr/bin/env python
"""
MIT License

Copyright (c) 2017 Raphael "rGunti" Guntersweiler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from datetime import datetime
from ConfigParser import ConfigParser
from os import environ
import pytz
import sys

STARTED_APP = 'APP'

TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f %Z%z'
LOGGING_SECTION = 'Logging'
LOGGING_OPTION_FILE = 'path'
LOGGING_OPTION_MODE = 'mode'


def log(msg):
    """
    Prints a message to stdout
    :param msg:
    """
    print("{} | {}".format(get_utc_now(), msg))


def get_utc_now():
    """
    Returns the current UTC time
    :return str:
    """
    return datetime.now(pytz.utc).strftime(TIMESTAMP_FORMAT)


def boot_print(app_name):
    """
    Prints a Boot message
    :param str app_name:
    """
    global STARTED_APP
    STARTED_APP = app_name.upper()
    log(" === STARTING {} === ".format(STARTED_APP))


def end_print(app_name=None):
    """
    Prints a final shutdown message
    :param str app_name:
    """
    log(" === {} ENDED === ".format(app_name if app_name else STARTED_APP))


def setup_std_logging(log_file, log_mode='a+'):
    """
    Sets up logging to a given file
    :param str log_file:
    :param str log_mode:
    """
    if environ.get('CARPI_LOG_TO_STDOUT', '0') != '1' and log_file:
        sys.stderr = open(log_file, log_mode)
        sys.stdout = sys.stderr


def init_logging_from_config(config):
    """
    Initializes Logging based on a Configuration File
    :param ConfigParser config:
    """
    if config.has_section(LOGGING_SECTION):
        if config.has_option(LOGGING_SECTION, LOGGING_OPTION_FILE):
            log_file = config.get(LOGGING_SECTION, LOGGING_OPTION_FILE)
            log_mode = 'a+'
            if config.has_option(LOGGING_SECTION, LOGGING_OPTION_MODE):
                log_mode = config.get(LOGGING_SECTION, LOGGING_OPTION_MODE)
            setup_std_logging(log_file, log_mode)


if __name__ == "__main__":
    log("This script is not intended to be run standalone!")
