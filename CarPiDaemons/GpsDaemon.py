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
from time import sleep

import pytz

from CarPiLogging import log, boot_print, end_print, get_utc_now, print_unhandled_exception, EXIT_CODES
from CarPiConfig import init_config_env
from CarPiThreading import CarPiThread
from RedisUtils import get_redis, set_piped, get_persistent_redis, incr_piped
from RedisKeys import GpsRedisKeys, PersistentGpsRedisKeys
from gps import gps, gpsfix, WATCH_ENABLE
from math import isnan
from geopy.distance import vincenty
from redis import exceptions as redis_exceptions
from sys import exit
import os


APP_NAME = os.path.basename(__file__)
GPS_POLLER = None

GPS_STOP_TIMEOUT_SECS = 3


class GpsPoller(CarPiThread):
    def __init__(self):
        CarPiThread.__init__(self, None)
        self._gps = gps(mode=WATCH_ENABLE)

    def _do(self):
        self._gps.next()

    def get_current_gps_data(self):
        return GpsPoint(self._gps)


class GpsPoint(object):
    def __init__(self, gps):
        """
        :param gps gps:
        """
        self._fix = gps.fix
        self._utc = gps.utc

    def get_fix(self):
        """
        Returns the GPS Fix data
        :return gpsfix:
        """
        return self._fix

    def get_utc_time(self):
        """
        Returns the GPS time in UTC
        :return:
        """
        return self._utc

    def convert_to_redis(self):
        """
        Returns a Dictionary prepared for storage in Redis
        :return:
        """
        return {
            GpsRedisKeys.KEY_FIX_MODE: self._fix.mode,
            GpsRedisKeys.KEY_LATITUDE: self._fix.latitude,
            GpsRedisKeys.KEY_LONGITUDE: self._fix.longitude,
            GpsRedisKeys.KEY_ALTITUDE: self._fix.altitude,
            GpsRedisKeys.KEY_EPX: self._fix.epx,
            GpsRedisKeys.KEY_EPY: self._fix.epy,
            GpsRedisKeys.KEY_EPV: self._fix.epv,
            GpsRedisKeys.KEY_EPT: self._fix.ept,
            GpsRedisKeys.KEY_EPD: self._fix.epd,
            GpsRedisKeys.KEY_EPS: self._fix.eps,
            GpsRedisKeys.KEY_EPC: self._fix.epc,
            GpsRedisKeys.KEY_TIME: self._utc,
            GpsRedisKeys.KEY_CLIMB: self._fix.climb,
            GpsRedisKeys.KEY_TRACK: self._fix.track,
            GpsRedisKeys.KEY_SPEED: self._fix.speed,
            GpsRedisKeys.KEY_SPEED_KMH: (self._fix.speed * 3.6),
            GpsRedisKeys.KEY_SPEED_MPH: (self._fix.speed * 2.23694),
            GpsRedisKeys.KEY_LAST_UPDATED: get_utc_now(),
            GpsRedisKeys.KEY_ALIVE: datetime.now(pytz.utc)
        }

    def get_lat_lon(self):
        """
        Returns Latitude and Longitude as a Tuple
        :return Tuple:
        """
        return self._fix.latitude, self._fix.longitude


if __name__ == "__main__":
    EXIT_CODE = EXIT_CODES['OK']

    CONFIG = init_config_env('CARPI_GPSD_CONF', ['gps-daemon.conf', '/etc/carpi/gps-daemon.conf'])
    boot_print(APP_NAME)

    CONFIG_DATAPOLLER_INTERVAL = CONFIG.getfloat('DataPoller', 'interval') / 1000
    CONFIG_RECORD_ODO = CONFIG.getboolean('ODO_Recording', 'enabled')

    log("Initializing GPS ...")
    GPS_POLLER = GpsPoller()
    GPS_POLLER.start()

    log("Initializing Redis Connection ...")
    R = get_redis(CONFIG)
    RP = get_persistent_redis(CONFIG)

    try:
        log("GPS Daemon is running ...")
        last_data = None
        while True:
            data = GPS_POLLER.get_current_gps_data().convert_to_redis()

            if CONFIG_RECORD_ODO and last_data:
                # Compare Fix
                old_fix = last_data.get(GpsRedisKeys.KEY_FIX_MODE, 0)
                new_fix = data.get(GpsRedisKeys.KEY_FIX_MODE, 0)
                if old_fix >= new_fix or (old_fix >= 2 and new_fix >= 2):
                    # Calculate Distance traveled and write to persistence (if > 0m)
                    old_xy = last_data.get(GpsRedisKeys.KEY_LATITUDE), last_data.get(GpsRedisKeys.KEY_LONGITUDE)
                    new_xy = data.get(GpsRedisKeys.KEY_LATITUDE), data.get(GpsRedisKeys.KEY_LONGITUDE)
                    if isnan(old_xy[0]) or isnan(new_xy[0]):
                        pass
                    else:
                        distance_traveled = vincenty(old_xy, new_xy).meters
                        if distance_traveled > 0:
                            incr_piped(RP, {
                                PersistentGpsRedisKeys.KEY_ODO: distance_traveled,
                                PersistentGpsRedisKeys.KEY_TRIP_A: distance_traveled,
                                PersistentGpsRedisKeys.KEY_TRIP_B: distance_traveled
                            })
                last_data = data
            else:
                last_data = data

            set_piped(R, data)
            sleep(CONFIG_DATAPOLLER_INTERVAL)
    except (KeyboardInterrupt, SystemExit):
        log("Shutdown requested!")
    except redis_exceptions.ConnectionError:
        EXIT_CODE = EXIT_CODES['DataDestinationLost']
        log("Connection to Redis Server lost! Daemon is quitting and waiting for relaunch")
    except:
        EXIT_CODE = EXIT_CODES['UnhandledException']
        print_unhandled_exception(APP_NAME)
    finally:
        if not GPS_POLLER.stop_safe() and EXIT_CODE == EXIT_CODES['OK']:
            EXIT_CODE = EXIT_CODES['BackgroundThreadTimedOut']

    end_print()
    exit(EXIT_CODE)
