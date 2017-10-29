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

from redis import Redis, exceptions
from CarPiLogging import log
from ConfigParser import ConfigParser
from threading import Thread
from time import sleep


# Config Sections and Keys
RCONFIG_SECTION = 'Redis'
RCONFIG_KEY_HOST = 'host'
RCONFIG_KEY_PORT = 'port'
RCONFIG_KEY_DB = 'db'


def get_redis(config):
    """
    :param ConfigParser config:
    :return Redis:
    """
    return Redis(host=config.get(RCONFIG_SECTION, RCONFIG_KEY_HOST),
                 port=config.getint(RCONFIG_SECTION, RCONFIG_KEY_PORT),
                 db=config.get(RCONFIG_SECTION, RCONFIG_KEY_DB),
                 socket_connect_timeout=5)


def get_piped(r, keys):
    """
    Creates a Pipeline and requests all listed items at once.
    Returns a dictionary with the key-value pairs being equivalent
    to the stored values in Redis.
    :param Redis r:
    :param list of str keys:
    :return dict of (str, str):
    """
    data_dict = {}
    pipe = r.pipeline()
    for key in keys:
        pipe.get(key)
        data_dict[key] = None

    data = pipe.execute()
    for i, item in enumerate(data):
        data_dict[keys[i]] = item

    return data_dict


def set_piped(r, data_dict):
    """
    Creates a Pipeline and sends all listed items at once.
    Returns a dictionary with the key-value pairs containing the
    result of each operation.
    :param Redis r:
    :param dict of (str, object) data_dict:
    :return dict of (str, str):
    """
    keys = []
    result_dict = {}
    pipe = r.pipeline()
    for key, value in data_dict.iteritems():
        pipe.set(key, value)
        result_dict[key] = None
        keys.append(key)

    data = pipe.execute()
    for i, item in enumerate(data):
        result_dict[keys[i]] = item

    return result_dict


class RedisBackgroundFetcher(Thread):
    """
    Redis Background Data Fetcher
    """

    RETRIES = 5
    RETRY_INTERVAL = 0.5

    def __init__(self, r, keys_to_fetch, fetch_interval=0.1):
        """
        :param Redis r:
        :param list of str keys_to_fetch:
        :param int fetch_interval:
        """
        super(RedisBackgroundFetcher, self).__init__()
        self.keys_to_fetch = keys_to_fetch
        self._r = r
        self._running = True
        self._interval = fetch_interval
        self._current_data = {}  # type: dict of (str, str)

        self._retries = RedisBackgroundFetcher.RETRIES

    def _fetch_data(self):
        # Creates a copy so a user interaction does not cause problems
        keys = self.keys_to_fetch[:]
        new_data = get_piped(self._r, keys)
        self._current_data = new_data

    def get_current_data(self):
        return self._current_data

    def run(self):
        while self._running:
            try:
                self._fetch_data()
                self._retries = RedisBackgroundFetcher.RETRIES
            except (exceptions.ConnectionError, exceptions.TimeoutError):
                if self._retries == 0:
                    log("Failed to reconnect to Redis after {} retries!".format(RedisBackgroundFetcher.RETRIES))
                    raise
                else:
                    log("Connection to Redis lost, skipping and trying again in {} seconds ({} more times) ..."
                        .format(RedisBackgroundFetcher.RETRY_INTERVAL, self._retries))
                    self._retries -= 1
                    sleep(RedisBackgroundFetcher.RETRY_INTERVAL)
            except SystemExit:
                log("SystemExit has been requested, stopping Fetcher Thread ...")
                self._running = False

            sleep(self._interval)

    def stop(self, timeout=None):
        self._running = False
        self.join(timeout=timeout)


if __name__ == "__main__":
    print("This script is not intended to be run standalone!")
