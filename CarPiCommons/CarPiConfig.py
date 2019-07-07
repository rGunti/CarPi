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
from ConfigParser import ConfigParser
from CarPiLogging import log, init_logging_from_config
from os import environ


class ConfigFileNotFoundError(Exception):
    pass


def init_config(filepath):
    """
    Creates a new ConfigParser instance and reads the given file
    :param str filepath: Configuration File's Path
    :return ConfigParser:
    """
    log('Reading Config File {} ...'.format(filepath))
    config = ConfigParser()
    try:
        config.readfp(open(filepath))
    except IOError:
        raise ConfigFileNotFoundError
    init_logging_from_config(config)
    return config


def init_config_env(env_name, default_names=['config.cnf']):
    """
    Creates a new ConfigParser instance and reads the file given
    by an Environmental Variable. If variable does not exist
    a default value will be used.
    :param str env_name: Name of Environmental Variable
    :param list of str default_names: Default Name (default: 'config.cnf')
    :return ConfigParser:
    """
    if env_name in environ:
        return init_config(environ[env_name])
    else:
        c = None
        for default_name in default_names:
            try:
                c = init_config(default_name)
                return c
            except ConfigFileNotFoundError:
                log('Could not find {} ...'.format(default_name))

        if not c:
            log('Failed to load Configuration File!')
            raise ConfigFileNotFoundError('Failed to load Configuration File!')
        else:
            # This will probably never happen...
            return c


if __name__ == "__main__":
    log("This script is not intended to be run standalone!")
