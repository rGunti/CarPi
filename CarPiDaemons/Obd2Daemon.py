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
from _socket import timeout
from telnetlib import Telnet
from time import sleep

from os import path

from CarPiConfig import init_config_env
from CarPiLogging import EXIT_CODES, boot_print, end_print, print_unhandled_exception, log
from CarPiThreading import CarPiThread
from Obd2DataParser import transform_obj, parse_obj
from RedisKeys import ObdRedisKeys
from RedisUtils import get_redis, set_piped
from redis import exceptions as redis_exceptions


APP_NAME = path.basename(__file__)


class ObdTelnetPoller(CarPiThread):
    def __init__(self, host='192.168.0.10', port=35000, init_sequence=[], poll_sequence=[]):
        CarPiThread.__init__(self, 0.01)
        self._data = None
        self._t = Telnet()

    def _do(self):
        new_data = {}

        self._data = new_data

    def get_current_data(self):
        return self._data


class ObdEnvConfigError(Exception):
    def __init__(self, sent_cmd, received_response):
        self.sent_cmd = sent_cmd
        self.received_response = received_response


def send(t, cmd):
    """
    :param Telnet t:
    :param str cmd:
    :return str:
    """
    log('Sending {}'.format(cmd))
    t.write('{}\r'.format(cmd))
    data = ''
    while '>' not in data:
        data = data + t.read_eager()
    log('{}: Received {} bytes'.format(cmd, len(data)))
    return data.replace('\r', '|').strip()


def get_arr(t, cmds):
    """
    :param Telnet t:
    :param list of str cmds:
    :return list of str:
    """
    log('Requesting {} items'.format(len(cmds)))
    o = {}
    for cmd in cmds:
        o[cmd] = send(t, cmd)
    return o


if __name__ == "__main__":
    EXIT_CODE = EXIT_CODES['OK']

    CONFIG = init_config_env('CARPI_OBD_CONF', ['obd-daemon.conf', '/etc/carpi/obd-daemon.conf'])
    boot_print(APP_NAME)

    CONFIG_OBD_HOST = CONFIG.get('PollerSource', 'host')
    CONFIG_OBD_PORT = CONFIG.getint('PollerSource', 'port')
    CONFIG_OBD_TIMEOUT = CONFIG.getint('PollerSource', 'timeout')
    CONFIG_OBD_RETRY_TIMEOUT = CONFIG.getint('PollerSource', 'retry_timeout')

    CONFIG_INIT_SEQ = CONFIG.get('DataPoller', 'init_sequence').split(',')
    CONFIG_POLL_SEQ = CONFIG.get('DataPoller', 'poll_sequence').split(',')

    log("Initialize Redis Connection ...")
    R = get_redis(CONFIG)

    T = None  # type: Telnet

    try:
        log("OBD Daemons is running ...")
        while True:
            T = Telnet()

            try:
                log("Connecting to OBD Adapter ...")
                T.open(host=CONFIG_OBD_HOST,
                       port=CONFIG_OBD_PORT,
                       timeout=CONFIG_OBD_TIMEOUT)

                log("Awaiting response ...")
                T.write('\r')
                T.read_until('>', timeout=CONFIG_OBD_TIMEOUT)

                log("Configuring Environment ...")
                for cmd in CONFIG_INIT_SEQ:
                    r = send(T, cmd)
                    if 'ERROR' in r:
                        raise ObdEnvConfigError(cmd, r)

                log("Configuration completed, starting recording loop ...")
                while True:
                    data = transform_obj(parse_obj(get_arr(T, CONFIG_POLL_SEQ)))
                    data[ObdRedisKeys.KEY_ALIVE] = 1
                    set_piped(R, data)
            except timeout:
                log("Connection to OBD Adapter timed out after {} sec, retrying after {} sec".format(
                    CONFIG_OBD_TIMEOUT, CONFIG_OBD_RETRY_TIMEOUT))
                set_piped(R, {ObdRedisKeys.KEY_ALIVE: 0})
                sleep(CONFIG_OBD_RETRY_TIMEOUT)
            except ObdEnvConfigError as e:
                log("Failed to configure environment (Sent={}, Received={})".format(e.sent_cmd,
                                                                                    e.received_response))
                set_piped(R, {ObdRedisKeys.KEY_ALIVE: 0})
                sleep(CONFIG_OBD_RETRY_TIMEOUT)
            finally:
                try:
                    log("Trying to close Telnet connection ...")
                    T.close()
                except (KeyboardInterrupt, SystemExit, redis_exceptions.ConnectionError) as e:
                    # Rethrow the important ones for good measure
                    raise e
                except:  # Just catch everything else when closing
                    pass
                finally:
                    T = None
    except (KeyboardInterrupt, SystemExit):
        log("Shutdown requested!")
    except redis_exceptions.ConnectionError:
        EXIT_CODE = EXIT_CODES['DataDestinationLost']
        log("Connection to Redis Server lost! Daemon is quitting and waiting for relaunch")
    except:
        EXIT_CODE = EXIT_CODES['UnhandledException']
        print_unhandled_exception()
    finally:
        if T:
            log("Trying to close Telnet connection ...")
            try:
                T.close()
            except:
                pass

    end_print()
    exit(EXIT_CODE)
