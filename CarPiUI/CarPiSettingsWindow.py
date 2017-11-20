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

from RedisKeys import NetworkInfoRedisKeys
from RedisUtils import RedisBackgroundFetcher
from pqGUI import Window, DECO_CLOSE, Scrollbar, VERTICAL, BG_COLOR, Container, Widget, BG_LIGHT, Text, Box, BD_COLOR


class CarPiSettingsWindow(Window):
    def __init__(self, parent, redis, icon=None):
        Window.__init__(self,
                        parent,
                        ((0, 19), (320, 220)),
                        'Settings',
                        icon=icon,
                        style={BG_COLOR: (100, 100, 100)},
                        buttons=DECO_CLOSE,
                        modal=False)
        self.restrict_position = True

        self._scrollbar = Scrollbar(self,
                                    ((304, -2), (16, 222)),
                                    style={BG_LIGHT: (25, 25, 25)},
                                    direction=VERTICAL).pack()
        self._container = Container(self,
                                    ((0, 0), (303, 220)),
                                    yscroll=self._scrollbar).pack()

        self._fetcher = RedisBackgroundFetcher(redis, [
            NetworkInfoRedisKeys.KEY_ETH0_IP,
            NetworkInfoRedisKeys.KEY_WLAN0_STRENGTH,
            NetworkInfoRedisKeys.KEY_WLAN0_SSID,
            NetworkInfoRedisKeys.KEY_WLAN0_IP,
            NetworkInfoRedisKeys.KEY_WLAN1_STRENGTH,
            NetworkInfoRedisKeys.KEY_WLAN1_SSID,
            NetworkInfoRedisKeys.KEY_WLAN1_IP
        ])
        self._fetcher.start()

        self._ethernet_ip = None  # type: Text
        self._wifi0_ip = None  # type: Text
        self._wifi1_ip = None  # type: Text

        self._last_updated = datetime.now()

        self._init_controls()

    def _init_controls(self):
        parent = self._container
        Text(parent, ((5, 5), (294, 20)), 'Networking Status').pack()
        Box(parent, ((5, 20), (294, 0)), style={BD_COLOR: (100, 100, 100)}).pack()

        Text(parent, ((15, 24), (284, 20)), 'Ethernet:').pack()
        Text(parent, ((15, 39), (284, 20)), 'WiFi Hotspot:').pack()
        Text(parent, ((15, 54), (284, 20)), 'WiFi External:').pack()

        self._ethernet_ip = Text(parent, ((100, 24), (200, 20)), '-').pack()
        self._wifi0_ip = Text(parent, ((100, 39), (200, 20)), '-').pack()
        self._wifi1_ip = Text(parent, ((100, 54), (200, 20)), '-').pack()

    def update(self):
        if (datetime.now() - self._last_updated).seconds > 1:
            new_data = self._fetcher.get_current_data()
            self._ethernet_ip.settext(new_data.get(NetworkInfoRedisKeys.KEY_ETH0_IP, '-'))
            self._wifi0_ip.settext(new_data.get(NetworkInfoRedisKeys.KEY_WLAN0_IP, '-'))
            self._wifi1_ip.settext(new_data.get(NetworkInfoRedisKeys.KEY_WLAN1_IP, '-'))

            self._last_updated = datetime.now()

    def destroy(self):
        self._fetcher.stop_safe(5)
        super(CarPiSettingsWindow, self).destroy()


if __name__ == "__main__":
    print("This script is not intended to be run standalone!")
