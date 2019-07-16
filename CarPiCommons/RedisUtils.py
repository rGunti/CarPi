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
from CarPiThreading import CarPiThread
from ConfigParser import ConfigParser, NoOptionError
from time import sleep


# Config Sections and Keys
RCONFIG_SECTION = 'Redis'
RCONFIG_PERSISTENT_SECTION = 'Persistent_Redis'
RCONFIG_KEY_HOST = 'host'
RCONFIG_KEY_PORT = 'port'
RCONFIG_KEY_DB = 'db'
RCONFIG_KEY_EXPIRE = 'expire'

RCONFIG_VALUE_EXPIRE = None
RCONFIG_VALUE_EXPIRE_COMMANDS = 5


def _get_redis(config, section):
    """
    :param ConfigParser config:
    :param str section:
    :return Redis:
    """
    return Redis(host=config.get(section, RCONFIG_KEY_HOST),
                 port=config.getint(section, RCONFIG_KEY_PORT),
                 db=config.get(section, RCONFIG_KEY_DB),
                 socket_connect_timeout=5)


def get_redis(config):
    """
    Returns the default Redis connection
    :param ConfigParser config:
    :return Redis:
    """
    global RCONFIG_VALUE_EXPIRE
    try:
        RCONFIG_VALUE_EXPIRE = config.getint(RCONFIG_SECTION, RCONFIG_KEY_EXPIRE)
        log("The Redis values will expire after {} seconds.".format(RCONFIG_VALUE_EXPIRE))
    except NoOptionError:
        log("The Redis values will not expire.")
        RCONFIG_VALUE_EXPIRE = None
    except ValueError:
        log("The provided default Expire value is invalid! No expiration will be set.")
        RCONFIG_VALUE_EXPIRE = None

    return _get_redis(config, RCONFIG_SECTION)


def get_persistent_redis(config):
    """
    Returns the Persistent Redis Connection
    :param ConfigParser config:
    :return Redis:
    """
    return _get_redis(config, RCONFIG_PERSISTENT_SECTION)


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
        if type(key) is tuple or type(key) is list:
            for i in range(len(key)):
                if value[i] is None:
                    pipe.delete(key[i])
                else:
                    pipe.set(key[i], value[i], ex=RCONFIG_VALUE_EXPIRE)

                result_dict[key[i]] = None
                keys.append(key[i])
        else:
            if value is None:
                pipe.delete(key)
            elif type(key) is tuple or type(key) is list:
                pipe.set(key, '|'.join(value), ex=RCONFIG_VALUE_EXPIRE)
            else:
                pipe.set(key, value, ex=RCONFIG_VALUE_EXPIRE)

            result_dict[key] = None
            keys.append(key)

    data = pipe.execute()
    for i, item in enumerate(data):
        result_dict[keys[i]] = item

    return result_dict


def incr_piped(r, data_dict):
    """
    Same as set_piped, but uses INCRBY instead of SET.
    Increases <key> by <value>.
    Note that INCRBY does not support expiration so this will
    not be taken into account
    :param Redis r:
    :param dict of (str, object) data_dict:
    :return dict of (str, str):
    """
    keys = []
    result_dict = {}
    pipe = r.pipeline()
    for key, value in data_dict.iteritems():
        if value is None:
            pipe.delete(key)
        else:
            pipe.incrbyfloat(key, value)

        result_dict[key] = None
        keys.append(key)

    data = pipe.execute()
    for i, item in enumerate(data):
        result_dict[keys[i]] = item

    return result_dict


def get_command_param_key(command, param_name):
    return command + '.Param:' + param_name


def send_command_request(r, command, params=None):
    """
    Creates a new Command Request and sends it to Redis for
    a request processor to process
    :param Redis r: Redis instance
    :param str command: Command Name
    :param dict of str, object params: Optional Command params
    :return:
    """
    pipe = r.pipeline()
    pipe.set(command, True, ex=RCONFIG_VALUE_EXPIRE_COMMANDS)
    if params:
        for key, value in params.iteritems():
            if value is not None:
                param_key = get_command_param_key(command, key)
                pipe.set(param_key, value, ex=RCONFIG_VALUE_EXPIRE_COMMANDS)

    pipe.execute()


def set_command_as_handled(r, command):
    """
    Removes a Command Request from Redis and thus marks it as handled
    :param Redis r: Redis instance
    :param str command: Command Name
    """
    pipe = r.pipeline()
    pipe.delete(command)
    pipe.execute()


def get_command_params(r, command, params, delete_after_request=True):
    """
    Returns one or more parameters of a given command
    :param Redis r: Redis instance
    :param str command: Command Name
    :param str|list of str params: Paramter Name or list of Parameter Names to request
    :param bool delete_after_request: If True, all requested parameters will be deleted after execution
    :return str|dict of str, str:
    """
    if isinstance(params, list):
        output = {}
        keys = []
        key_map = {}

        for key in params:
            output[key] = None
            param_key = get_command_param_key(command, key)
            keys.append(param_key)
            key_map[param_key] = key

        out = get_piped(r, keys)

        for key, value in out.iteritems():
            output[key_map[key]] = value

        if delete_after_request:
            pipe = r.pipeline()
            for key in keys:
                r.delete(key)
            pipe.execute()

        return output
    else:
        return r.get(get_command_param_key(command, params))


def load_synced_value(r, pr, key):
    """
    :param Redis r: Redis instance
    :param Redis pr: Persistent Redis instance
    :param str key:
    :return str:
    """
    o = get_piped(pr, [key])
    if key in o and o[key]:
        set_piped(r, {key: o[key]})
        return o[key]
    else:
        r.delete(key)
        return None


def save_synced_value(r, pr, key, value):
    """
    :param Redis r: Redis instance
    :param Redis pr: Persistent Redis instance
    :param str key:
    :param str|None value:
    :return str:
    """
    if value:
        s = {key: value}
        set_piped(r, s)
        set_piped(pr, s)
    else:
        r.delete(key)
        pr.delete(key)


def check_command_requests(r, commands):
    """
    Checks a list of commands for a pending request
    :param Redis r: Redis instance
    :param list of str commands: List of Commands
    :return:
    """
    return get_piped(r, commands)


class RedisBackgroundFetcher(CarPiThread):
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
        CarPiThread.__init__(self, fetch_interval)
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

    def _do(self):
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


class CarPiControlThread(CarPiThread):
    def __init__(self, redis, commands, parameters, interval):
        """
        :param Redis redis: Redis instance
        :param list of str commands:
        :param dict of str, list of str parameters:
        :param int|float interval:
        """
        CarPiThread.__init__(self, interval)
        self._redis = redis
        self._commands = commands  # type: list str
        self._parameters = parameters  # type: dict str, list str

        self._command_implementation = self._map_command_implementations(commands)  # type: dict str, function

    def _map_command_implementations(self, commands):
        """
        :param list of str commands:
        :return dict of str, function:
        """
        raise NotImplementedError

    def _do(self):
        commands_to_execute = {}

        # Get all commands which are requested
        requested_commands = check_command_requests(self._redis, self._commands)
        for command, val in requested_commands.iteritems():
            if not val:
                continue
            if command in self._parameters:
                # Get Parameter Values
                params = self._parameters[command]
                commands_to_execute[command] = get_command_params(self._redis,
                                                                  command,
                                                                  params)
            else:
                # Execute without Parameters
                commands_to_execute[command] = True

        # Execute Commands
        for command, params in commands_to_execute.iteritems():
            if isinstance(params, dict):
                self._execute_command(command, params)
            else:
                self._execute_command(command)
            set_command_as_handled(self._redis, command)

    def _execute_command(self, command, params=None):
        if command in self._command_implementation:
            fun = self._command_implementation[command]
            if params:
                fun(params)
            else:
                fun()
        else:
            log("No function found for Redis Command {}!".format(command))


if __name__ == "__main__":
    print("This script is not intended to be run standalone!")
