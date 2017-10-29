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


class GpsRedisKeys:
    KEY_LATITUDE = 'GPS.Latitude'  # type: str
    KEY_LONGITUDE = 'GPS.Longitude'  # type: str
    KEY_ALTITUDE = 'GPS.Altitude'  # type: str
    KEY_FIX_MODE = 'GPS.FixMode'  # type: str
    KEY_EPX = 'GPS.EPX'  # type: str
    KEY_EPY = 'GPS.EPY'  # type: str
    KEY_EPV = 'GPS.EPV'  # type: str
    KEY_EPT = 'GPS.EPT'  # type: str
    KEY_EPD = 'GPS.EPD'  # type: str
    KEY_EPS = 'GPS.EPS'  # type: str
    KEY_EPC = 'GPS.EPC'  # type: str
    KEY_TIME = 'GPS.Time'  # type: str
    KEY_CLIMB = 'GPS.Climb'  # type: str
    KEY_TRACK = 'GPS.Track'  # type: str
    KEY_SPEED = 'GPS.Speed'  # type: str
    KEY_SPEED_KMH = 'GPS.Speed.KMH'  # type: str
    KEY_SPEED_MPH = 'GPS.Speed.MPH'  # type: str
    KEY_LAST_UPDATED = 'GPS.LastUpdated'  # type: str

    KEYS = [
        KEY_LATITUDE,
        KEY_LONGITUDE,
        KEY_ALTITUDE,
        KEY_FIX_MODE,
        KEY_EPX,
        KEY_EPY,
        KEY_EPV,
        KEY_EPT,
        KEY_EPD,
        KEY_EPS,
        KEY_EPC,
        KEY_TIME,
        KEY_CLIMB,
        KEY_TRACK,
        KEY_SPEED,
        KEY_SPEED_KMH,
        KEY_SPEED_MPH,
        KEY_LAST_UPDATED
    ]


class NetworkInfoRedisKeys:
    KEY_ETH0_IP = 'Net.eth0.IP'
    KEY_WLAN0_IP = 'Net.wlan0.IP'
    KEY_WLAN0_STRENGTH = 'Net.wlan0.Strength'
    KEY_WLAN0_SSID = 'Net.wlan0.SSID'
    KEY_WLAN1_IP = 'Net.wlan1.IP'
    KEY_WLAN1_STRENGTH = 'Net.wlan1.Strength'
    KEY_WLAN1_SSID = 'Net.wlan1.SSID'

    KEYS = [
        KEY_ETH0_IP,
        KEY_WLAN0_IP,
        KEY_WLAN0_STRENGTH,
        KEY_WLAN0_SSID,
        KEY_WLAN1_IP,
        KEY_WLAN1_STRENGTH,
        KEY_WLAN1_SSID
    ]


def prepare_dict(keys, default_value=None):
    dict = {}
    for key in keys:
        dict[key] = default_value
    return dict


if __name__ == "__main__":
    print("This script is not intended to be run standalone!")
