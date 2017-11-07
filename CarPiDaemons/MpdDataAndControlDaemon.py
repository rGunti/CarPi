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
from os import path
from sys import exit
from time import sleep

import pytz
from mpd import MPDClient, ConnectionError

from CarPiConfig import init_config_env
from CarPiLogging import EXIT_CODES, boot_print, end_print, log, print_unhandled_exception
from CarPiThreading import CarPiThread
from CarPiUtils import format_mpd_status_time
from RedisKeys import MpdDataRedisKeys
from RedisUtils import get_redis, set_piped
from redis import exceptions as redis_exceptions

APP_NAME = path.basename(__file__)


class MpdDataPoller(CarPiThread):
    def __init__(self, config, interval):
        """
        :param ConfigParser.ConfigParser config:
        :param int interval:
        """
        CarPiThread.__init__(self, interval)
        self._mpd = self._init_mpd(config)
        self._data = {}

    def _init_mpd(self, config):
        """
        :param ConfigParser.ConfigParser config:
        :return MPDClient:
        """
        CONFIG_MPD_HOST = config.get('MPD', 'host')
        CONFIG_MPD_PORT = config.getint('MPD', 'port')
        CONFIG_MPD_TIMEOUT = config.getint('MPD', 'timeout')

        mpd = MPDClient()
        mpd.timeout = CONFIG_MPD_TIMEOUT
        mpd.idletimeout = None
        mpd.connect(CONFIG_MPD_HOST, CONFIG_MPD_PORT, CONFIG_MPD_TIMEOUT)
        return mpd

    def _do(self):
        mpd_status = self._mpd.status()  # type: dict str, any
        current_song = self._mpd.currentsong()  # type: dict str, any
        mpd_time = mpd_status.get('time', '0:0')
        current_song_length = current_song.get('time', '0')
        new_data = {
            MpdDataRedisKeys.KEY_ALIVE: datetime.now(pytz.utc),
            MpdDataRedisKeys.KEY_STATE: mpd_status.get('state', 'no_status'),
            MpdDataRedisKeys.KEY_SONG_TITLE: current_song.get('title', ''),
            MpdDataRedisKeys.KEY_SONG_ARTIST: current_song.get('artist', ''),
            MpdDataRedisKeys.KEY_SONG_ALBUM: current_song.get('album', ''),
            MpdDataRedisKeys.KEY_SONG_LENGTH: current_song_length,
            MpdDataRedisKeys.KEY_SONG_LENGTH_FORMATTED: format_mpd_status_time(current_song_length, False),
            MpdDataRedisKeys.KEY_CURRENT_TIME: mpd_time,
            MpdDataRedisKeys.KEY_CURRENT_TIME_FORMATTED: format_mpd_status_time(mpd_time, True),
            MpdDataRedisKeys.KEY_VOLUME: int(mpd_status.get('volume', '100')),
            MpdDataRedisKeys.KEY_RANDOM: mpd_status.get('random', '0'),
            MpdDataRedisKeys.KEY_REPEAT: mpd_status.get('repeat', '0')
        }

        self._data = new_data

    def get_current_data(self):
        return self._data


def delete_alive_key(r):
    """
    :param Redis r:
    """
    try:
        log("Deleting Alive Key ...")
        r.delete(MpdDataRedisKeys.KEY_ALIVE)
    finally:
        pass


if __name__ == "__main__":
    EXIT_CODE = EXIT_CODES['OK']

    CONFIG = init_config_env('CARPI_NETD_CONF', ['mpd-daemon.conf', '/etc/carpi/mpd-daemon.conf'])
    boot_print(APP_NAME)

    CONFIG_DATAPOLLER_INTERVAL = CONFIG.getfloat('DataPoller', 'interval') / 1000

    log("Connecting to MPD ...")
    MPD_DATA_THREAD = MpdDataPoller(CONFIG, CONFIG_DATAPOLLER_INTERVAL)
    MPD_DATA_THREAD.start()

    log("Initializing Redis Connection ...")
    R = get_redis(CONFIG)

    try:
        log("MPD Data & Control Daemon is running ...")
        while True:
            current_data = MPD_DATA_THREAD.get_current_data()
            if current_data:
                set_piped(R, current_data)
            sleep(CONFIG_DATAPOLLER_INTERVAL)
    except (KeyboardInterrupt, SystemExit):
        log("Shutdown requested!")
    except ConnectionError:
        EXIT_CODE = EXIT_CODES['DataSourceLost']
        log("Connecting to MPD server lost, restarting daemon and trying again ...")
    except redis_exceptions.ConnectionError:
        EXIT_CODE = EXIT_CODES['DataDestinationLost']
        log("Connection to Redis Server lost! Daemon is quitting and waiting for relaunch")
    except:
        EXIT_CODE = EXIT_CODES['UnhandledException']
        print_unhandled_exception()
    finally:
        delete_alive_key(R)
        MPD_DATA_THREAD.stop_safe(5)

    end_print()
    exit(EXIT_CODE)
