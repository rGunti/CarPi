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

from pqGUI import *
from PygameUtils import load_image, init_pygame
from CarPiLogging import log, boot_print, end_print, print_unhandled_exception, EXIT_CODES
from CarPiConfig import init_config_env
from RedisUtils import get_redis, RedisBackgroundFetcher
from RedisKeys import GpsRedisKeys, NetworkInfoRedisKeys
from math import isnan
from redis import exceptions as redis_exceptions
from datetime import datetime
import os
import sys
import time

log("FBDEV: " + os.environ.get("SDL_FBDEV", '<nodev>'))
log("MOUSE: [" + os.environ.get("SDL_MOUSEDRV", '<nodrv>') + "] " + os.environ.get("SDL_MOUSEDEV", '<nodev>'))

APP_NAME = os.path.basename(__file__)

EXIT_CODE = EXIT_CODES['OK']

FONT_DEFAULT = os.path.join('res', 'fonts', 'Vera.ttf')
FONT_7SEGM = os.path.join('res', 'fonts', 'DigitalCounter7.ttf')
FONT_DOTMTX = os.path.join('res', 'fonts', 'scoreboard.ttf')

IMAGE_GPSSAT_OFF = os.path.join('res', 'img', 'gpssat-off.png')
IMAGE_GPSSAT_OK = os.path.join('res', 'img', 'gpssat-ok.png')
IMAGE_GPSSAT_WARN = os.path.join('res', 'img', 'gpssat-warn.png')
IMAGE_GPSSAT_ERROR = os.path.join('res', 'img', 'gpssat-error.png')
IMAGE_CAR_OFF = os.path.join('res', 'img', 'car-off.png')
IMAGE_CAR_OK = os.path.join('res', 'img', 'car-ok.png')
IMAGE_CAR_ERROR = os.path.join('res', 'img', 'car-error.png')
IMAGE_ETHERNET_OFF = os.path.join('res', 'img', 'ethernet-off.png')
IMAGE_ETHERNET = os.path.join('res', 'img', 'ethernet-ok.png')
IMAGE_WIFI_OFF = os.path.join('res', 'img', 'wifi-off.png')
IMAGE_WIFI0 = os.path.join('res', 'img', 'wifi0.png')
IMAGE_WIFI1 = os.path.join('res', 'img', 'wifi1.png')
IMAGE_WIFI2 = os.path.join('res', 'img', 'wifi2.png')
IMAGE_WIFI3 = os.path.join('res', 'img', 'wifi3.png')

IMAGES = {}

AUTOLOAD_IMAGES = [
    IMAGE_GPSSAT_OFF,
    IMAGE_GPSSAT_OK,
    IMAGE_GPSSAT_WARN,
    IMAGE_GPSSAT_ERROR,
    IMAGE_CAR_OFF,
    IMAGE_CAR_OK,
    IMAGE_CAR_ERROR,
    IMAGE_ETHERNET_OFF,
    IMAGE_ETHERNET,
    IMAGE_WIFI_OFF,
    IMAGE_WIFI0,
    IMAGE_WIFI1,
    IMAGE_WIFI2,
    IMAGE_WIFI3
]

RNAME_FETCH_KEYS = [
    GpsRedisKeys.KEY_FIX_MODE,
    GpsRedisKeys.KEY_LATITUDE,
    GpsRedisKeys.KEY_LONGITUDE,
    GpsRedisKeys.KEY_SPEED_KMH,
    GpsRedisKeys.KEY_EPX,
    GpsRedisKeys.KEY_EPY,

    NetworkInfoRedisKeys.KEY_ETH0_IP,
    NetworkInfoRedisKeys.KEY_WLAN0_IP,
    NetworkInfoRedisKeys.KEY_WLAN0_STRENGTH,
    NetworkInfoRedisKeys.KEY_WLAN1_IP,
    NetworkInfoRedisKeys.KEY_WLAN1_STRENGTH
]


class GpsApp(pqApp):
    def __init__(self, rect, title, style=None, fullscreen=False):
        super(GpsApp, self).__init__(rect, title, style, fullscreen)

        #self._testButton = Button(self,
        #                          ((20, 20), (100, 26)),
        #                          'Open Modal',
        #                          command=self._testButton_Click,
        #                          style=None)
        #self._testButton.pack()

        self._speedLabel = Text(self,
                                ((70, 10), (260, 195)),
                                '123',
                                style={
                                    TEXT_FONT: (FONT_7SEGM, 150),
                                    TEXT_COLOR: (200, 200, 200)
                                },
                                wrap=WRAP_CHAR).pack()

        self._speedUnitLabel = Text(self,
                                    ((230, 150), (95, 50)),
                                    'km/h',
                                    style={
                                        TEXT_FONT: (FONT_DOTMTX, 40),
                                        TEXT_COLOR: (200, 200, 200)
                                    },
                                    wrap=WRAP_CHAR).pack()

        # self._latitudeLabel = Text(self,
        #                            ((5, 150), (215, 40)),
        #                            '---.---------- N',
        #                            style={
        #                                TEXT_FONT: (FONT_DOTMTX, 20)
        #                            },
        #                            wrap=WRAP_CHAR).pack()
        #
        # self._longitudeLabel = Text(self,
        #                             ((5, 170), (215, 40)),
        #                             '---.---------- E',
        #                             style={
        #                                 TEXT_FONT: (FONT_DOTMTX, 20)
        #                             },
        #                             wrap=WRAP_CHAR).pack()

        self._speedGraph = Graph(self,
                                 ((5, 150), (215, 50)),
                                 data_gap_ms=500,
                                 style={
                                     TEXT_COLOR: (150, 150, 150)
                                 }).pack()
        self._speedGraph.prefill_data()

        self._accuracyLabel = Text(self,
                                   ((10, 45), (32, 32)),
                                   '---',
                                   style={
                                       TEXT_FONT: (FONT_DOTMTX, 15)
                                   },
                                   wrap=WRAP_CHAR).pack()

        # Status Icons
        self._gpsStatusIcon = Image(self, ((10, 10), (32, 32)), IMAGES[IMAGE_GPSSAT_OFF]).pack()
        self._carStatusIcon = Image(self, ((10, 75), (32, 32)), IMAGES[IMAGE_CAR_OFF]).pack()

        # Menu Bar
        Widget(self,
               rect=((0, 205), (320, 35)),
               style={BD_TYPE: BD_FLAT, BD_COLOR: (100, 100, 100), BG_COLOR: (0, 0, 0)}).pack()

        self._menuButton = Button(self,
                                  ((5, 210), (50, 25)),
                                  'Menu',
                                  self._menuButton_Click).pack()

        self._popup = Popup(self._menuButton)
        self._popup.additem('Ver. 0.1', None, state=DISABLED)
        self._popup.additem('Test Window', self._testButton_Click)
        self._popup.additem('Exit', self._closeButton_Click)

        # Menu Bar Status Icons
        self._ethernetStatusIcon = Image(self, ((145, 207), (32, 32)), IMAGES[IMAGE_ETHERNET_OFF]).pack()
        self._wifi0StatusIcon = Image(self, ((175, 207), (32, 32)), IMAGES[IMAGE_WIFI_OFF]).pack()
        self._wifi1StatusIcon = Image(self, ((205, 207), (32, 32)), IMAGES[IMAGE_WIFI_OFF]).pack()

        # Time Label in Status Bar
        self._timeLabel = Text(self,
                               ((230, 212), (95, 34)),
                               '00:00:00',
                               style={
                                   TEXT_FONT: (FONT_DOTMTX, 20)
                               },
                               wrap=WRAP_CHAR).pack()

        self._modal = Window(self,
                             ((50, 50), (150, 70)),
                             # ((0, 21), (320, 219)),
                             'This is a modal dialog',
                             style=None,
                             icon=None,
                             buttons=DECO_CLOSE)
        self._modal.restrict_position = True
        Text(self._modal,
             ((5, 5), (100, 100)),
             'This is text in the modal').pack()

        self.R_FETCH = None  # type: RedisBackgroundFetcher

    def main(self):
        pass

    def update(self):
        self._timeLabel.settext(time.strftime('%H:%M:%S'))

        current_data = self.R_FETCH.get_current_data()
        # if self._check_key(current_data, GpsRedisKeys.KEY_LATITUDE):
        #     self._set_latitude(current_data[GpsRedisKeys.KEY_LATITUDE])
        # else:
        #     self._set_latitude(-360)
        #
        # if self._check_key(current_data, GpsRedisKeys.KEY_LONGITUDE):
        #     self._set_longitude(current_data[GpsRedisKeys.KEY_LONGITUDE])
        # else:
        #     self._set_longitude(-360)

        if self._check_key(current_data, GpsRedisKeys.KEY_SPEED_KMH):
            self._set_speed(current_data[GpsRedisKeys.KEY_SPEED_KMH], False)
        else:
            self._set_speed(-1)

        if self._check_key(current_data, GpsRedisKeys.KEY_EPX) \
            and self._check_key(current_data, GpsRedisKeys.KEY_EPY) \
            and self._check_key(current_data, GpsRedisKeys.KEY_FIX_MODE):
            self._set_accuracy(val_x=current_data[GpsRedisKeys.KEY_EPX],
                               val_y=current_data[GpsRedisKeys.KEY_EPY],
                               mode=current_data[GpsRedisKeys.KEY_FIX_MODE])
        else:
            self._set_accuracy(-1, -1, 1)

        if self._check_key(current_data, NetworkInfoRedisKeys.KEY_ETH0_IP):
            self._ethernetStatusIcon.image = IMAGES[IMAGE_ETHERNET]
        else:
            self._ethernetStatusIcon.image = IMAGES[IMAGE_ETHERNET_OFF]

        wlan0_state = current_data.get(NetworkInfoRedisKeys.KEY_WLAN0_STRENGTH, '0')
        wlan1_state = current_data.get(NetworkInfoRedisKeys.KEY_WLAN1_STRENGTH, '0')

        if wlan0_state:
            self._set_wifi(self._wifi0StatusIcon,
                           self._check_key(current_data, NetworkInfoRedisKeys.KEY_WLAN0_IP),
                           int(wlan0_state))
        else:
            self._set_wifi(self._wifi0StatusIcon, False, 0)

        if wlan1_state:
            self._set_wifi(self._wifi1StatusIcon,
                           self._check_key(current_data, NetworkInfoRedisKeys.KEY_WLAN1_IP),
                           int(wlan1_state))
        else:
            self._set_wifi(self._wifi1StatusIcon, False, 0)

    @staticmethod
    def _check_key(data, key):
        return key in data and data[key] is not None

    def _set_speed(self, val, imperial=False):
        try:
            f_val = float(val)
            if isnan(f_val) or (val == -1):
                self._speedLabel.settext('  0')
                self._speedGraph.add_data_point(0)
            else:
                self._speedLabel.settext('{:>3.0f}'.format(f_val))
                self._speedGraph.add_data_point(f_val)
        except (ValueError, TypeError):
            log('Speed given could not be converted to float: {}'.format(val))
            self._speedLabel.settext('  0')
            self._speedGraph.add_data_point(0)

        # self._speedGraph.add_data_point(datetime.now().second)
        self._speedUnitLabel.settext(' mph' if imperial else 'km/h')

    def _set_latitude(self, val):
        try:
            f_val = float(val)
            if isnan(f_val) or (f_val == -360):
                self._latitudeLabel.settext('---.--------- -')
            else:
                self._latitudeLabel.settext('{:>13.9f} {}'.format(abs(f_val), 'S' if val < 0 else 'N'))
        except (ValueError, TypeError):
            log('Latitude given could not be converted to float: {}'.format(val))
            self._latitudeLabel.settext('---.--------- -')

    def _set_longitude(self, val):
        try:
            f_val = float(val)
            if isnan(f_val) or (f_val == -360):
                self._longitudeLabel.settext('---.--------- -')
            else:
                self._longitudeLabel.settext('{:>13.9f} {}'.format(abs(f_val), 'W' if val < 0 else 'E'))
        except (ValueError, TypeError):
            log('Longitude given could not be converted to float: {}'.format(val))
            self._longitudeLabel.settext('---.--------- -')

    def _set_accuracy(self, val_x, val_y, mode):
        try:
            f_val_x = float(val_x)
            f_val_y = float(val_y)
            i_val_m = int(float(mode))

            if f_val_x < 0 or f_val_y < 0:
                # No Data
                self._gpsStatusIcon.image = IMAGES[IMAGE_GPSSAT_OFF]
                self._accuracyLabel.settext('---')
            else:
                if i_val_m <= 1 or i_val_m > 3:
                    # No Fix / Invalid Data
                    self._gpsStatusIcon.image = IMAGES[IMAGE_GPSSAT_ERROR]
                    self._accuracyLabel.settext('FIX')
                else:
                    fix_accuracy = (f_val_x + f_val_y) / 2
                    if i_val_m == 2:
                        # 2D FIX
                        self._gpsStatusIcon.image = IMAGES[IMAGE_GPSSAT_WARN]
                    elif i_val_m == 3:
                        # 3D Fix
                        self._gpsStatusIcon.image = IMAGES[IMAGE_GPSSAT_OK]
                    self._accuracyLabel.settext('{:>3.0f}'.format(min(fix_accuracy, 999)))

        except (ValueError, TypeError):
            log('Failed to parse EPX, EPY or MODE: {} / {} / {}'.format(val_x, val_y, mode))
            self._gpsStatusIcon.image = IMAGES[IMAGE_GPSSAT_OFF]
            self._accuracyLabel.settext('ERR')

    def _set_ethernet(self, connected):
        self._ethernetStatusIcon.image = IMAGES[IMAGE_ETHERNET if connected else IMAGE_ETHERNET_OFF]

    def _set_wifi(self, wifi, connected, strength):
        """
        :param Image wifi:
        :param boolean connected:
        :param int strength:
        :return:
        """
        if connected:
            image = IMAGE_WIFI_OFF
            if strength > 75:
                image = IMAGE_WIFI3
            elif strength > 50:
                image = IMAGE_WIFI2
            elif strength > 25:
                image = IMAGE_WIFI1
            elif strength < 0:
                image = IMAGE_WIFI3
            else:
                image = IMAGE_WIFI0
            wifi.image = IMAGES[image]
        else:
            wifi.image = IMAGES[IMAGE_WIFI_OFF]

    def _testButton_Click(self, e):
        self._modal.show()

    def _closeButton_Click(self, e):
        self.exit()

    def _menuButton_Click(self, e):
        self._popup.show((self._menuButton.x, self._menuButton.y - self._popup.height))


if __name__ == '__main__':
    CONFIG = init_config_env('CARPI_UI_CONFIG', ['ui.conf', '/etc/carpi/ui.conf'])
    boot_print(APP_NAME)

    log("Connecting to Redis ...")
    R = get_redis(CONFIG)

    log("Starting Background Data Fetcher ...")
    R_FETCH = RedisBackgroundFetcher(R, RNAME_FETCH_KEYS)
    R_FETCH.start()

    init_pygame()

    log("Loading Assets ...")
    for image in AUTOLOAD_IMAGES:
        IMAGES[image] = load_image(image)

    log("Initializing UI App ...")
    app = GpsApp(rect=(320, 219),
                 title='CarPi GPS',
                 fullscreen=('NO_FULLSCREEN' not in os.environ))
    app.R_FETCH = R_FETCH
    try:
        log("Starting UI App ...")
        app.run()
    except (KeyboardInterrupt, SystemExit):
        log("Shutdown requested")
    except redis_exceptions.ConnectionError:
        EXIT_CODE = EXIT_CODES['DataSourceLost']
        log("Lost connection to Redis after retrying multiple times!")
    except:
        EXIT_CODE = EXIT_CODES['UnhandledException']
        print_unhandled_exception()
    finally:
        log("Shutting down UI ...")
        try:
            app.destroy()
        finally:
            pass

        log("Shutting down Fetcher ...")
        R_FETCH.stop_safe()

        end_print(APP_NAME)
        sys.exit(EXIT_CODE)
