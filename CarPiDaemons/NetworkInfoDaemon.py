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
from CarPiThreading import CarPiThread
from CarPiConfig import init_config_env
from CarPiLogging import log, boot_print, end_print, EXIT_CODES, print_unhandled_exception
from RedisUtils import get_redis, set_piped
from RedisKeys import NetworkInfoRedisKeys, prepare_dict
from redis import exceptions as redis_exceptions
from sys import exit
from os import path
from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM
from array import array
from struct import pack, unpack
from fcntl import ioctl
from subprocess import Popen, PIPE
from datetime import datetime
import pytz

APP_NAME = path.basename(__file__)


class NetDataPoller(CarPiThread):
    def __init__(self, interval):
        CarPiThread.__init__(self, interval)
        self._data = None

    def _do(self):
        new_data = {}

        # Get Interfaces and IP addresses
        ifaces = NetDataPoller._get_all_interfaces()
        for iface in ifaces:
            new_data[iface[0]] = NetDataPoller._format_ip(iface[1])

        self._data = new_data

    @staticmethod
    def _get_all_interfaces():
        max_pos = 128
        max_bytes = max_pos * 128

        s = socket(AF_INET, SOCK_DGRAM)
        names = array('B', '\0' * max_bytes)

        outbytes = unpack('iL', ioctl(
            s.fileno(),
            0x8912,
            pack('iL', max_bytes, names.buffer_info()[0])
        ))[0]
        namestr = names.tostring()

        lst = []
        for i in range(0, outbytes, 40):
            name = namestr[i:i+16].split('\0', 1)[0]
            ip = namestr[i + 20:i + 24]
            lst.append((name, ip))

        return lst

    @staticmethod
    def _format_ip(addr):
        return str(ord(addr[0])) + '.' + \
               str(ord(addr[1])) + '.' + \
               str(ord(addr[2])) + '.' + \
               str(ord(addr[3]))

    def get_current_data(self):
        return self._data


def get_iface_address(ifaces, iface_alias):
    if iface_alias in ifaces:
        return ifaces[iface_alias]
    else:
        return None


def extract_data(line, catch_string, length=None, remove_quotes=True):
    """
    :param str line:
    :param str catch_string:
    :param int length:
    :param boolean has_quotes:
    :return str:
    """
    start_idx = line.index(catch_string)
    value = line[start_idx + len(catch_string):]
    if length:
        value = value[:length]

    value = value.strip()

    if remove_quotes and '"' in value:
        value = value.strip('"')

    return value


def get_iface_signal_data(iface):
    data = {
        'iface': iface,
        'strength': -1,
        'ssid': None
    }
    cmd = Popen('iwconfig {}'.format(iface),
                shell=True,
                stdout=PIPE,
                stderr=PIPE)

    for line in cmd.stderr:
        if 'No such device' in line:
            return None

    for line in cmd.stdout:
        if 'no wireless extensions' in line:
            return None
        if 'Link Quality=' in line:
            strength = extract_data(line, 'Link Quality=', length=5)
            s_A = float(strength.split('/')[0])
            s_B = float(strength.split('/')[1])
            data['strength'] = int((s_A / s_B) * 100)
        if 'Not-Associated' in line:
            data['strength'] = 0
        if 'ESSID:' in line:
            ssid = extract_data(line, 'ESSID:')
            if ssid == 'off/any':
                ssid = None
            data['ssid'] = ssid

    # print(data)
    return data


if __name__ == "__main__":
    EXIT_CODE = EXIT_CODES['OK']

    CONFIG = init_config_env('CARPI_NETD_CONF', ['net-daemon.conf', '/etc/carpi/net-daemon.conf'])
    boot_print(APP_NAME)

    CONFIG_DATAPOLLER_INTERVAL = CONFIG.getfloat('DataPoller', 'interval') / 1000
    CONFIG_IFACE_ALIAS_ETH0 = CONFIG.get('Interface_Alias', 'eth0')
    CONFIG_IFACE_ALIAS_WLAN0 = CONFIG.get('Interface_Alias', 'wlan0')
    CONFIG_IFACE_ALIAS_WLAN1 = CONFIG.get('Interface_Alias', 'wlan1')

    log("Starting Data Poller ...")
    POLLER = NetDataPoller(CONFIG_DATAPOLLER_INTERVAL)
    POLLER.start()

    log("Initialize Redis Connection ...")
    R = get_redis(CONFIG)

    try:
        log("Network Info Daemon is running ...")
        while True:
            ips = POLLER.get_current_data()
            if ips:
                r_data = prepare_dict(NetworkInfoRedisKeys.KEYS)

                if CONFIG_IFACE_ALIAS_ETH0:
                    ip = get_iface_address(ips, CONFIG_IFACE_ALIAS_ETH0)
                    r_data[NetworkInfoRedisKeys.KEY_ETH0_IP] = ip

                if CONFIG_IFACE_ALIAS_WLAN0:
                    ip = get_iface_address(ips, CONFIG_IFACE_ALIAS_WLAN0)
                    wifi_data = get_iface_signal_data(CONFIG_IFACE_ALIAS_WLAN0)

                    r_data[NetworkInfoRedisKeys.KEY_WLAN0_IP] = ip
                    if wifi_data:
                        r_data[NetworkInfoRedisKeys.KEY_WLAN0_STRENGTH] = wifi_data['strength']
                        r_data[NetworkInfoRedisKeys.KEY_WLAN0_SSID] = wifi_data['ssid']

                if CONFIG_IFACE_ALIAS_WLAN1:
                    ip = get_iface_address(ips, CONFIG_IFACE_ALIAS_WLAN1)
                    wifi_data = get_iface_signal_data(CONFIG_IFACE_ALIAS_WLAN1)

                    r_data[NetworkInfoRedisKeys.KEY_WLAN1_IP] = ip
                    if wifi_data:
                        r_data[NetworkInfoRedisKeys.KEY_WLAN1_STRENGTH] = wifi_data['strength']
                        r_data[NetworkInfoRedisKeys.KEY_WLAN1_SSID] = wifi_data['ssid']

                r_data[NetworkInfoRedisKeys.KEY_ALIVE] = datetime.now(pytz.utc)
                set_piped(R, r_data)
            sleep(CONFIG_DATAPOLLER_INTERVAL)
    except (KeyboardInterrupt, SystemExit):
        log("Shutdown requested!")
    except redis_exceptions.ConnectionError:
        EXIT_CODE = EXIT_CODES['DataDestinationLost']
        log("Connection to Redis Server lost! Daemon is quitting and waiting for relaunch")
    except:
        EXIT_CODE = EXIT_CODES['UnhandledException']
        print_unhandled_exception()
    finally:
        POLLER.stop_safe()

    end_print()
    exit(EXIT_CODE)
