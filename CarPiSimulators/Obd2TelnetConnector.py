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
from __future__ import print_function

import socket
import telnetlib
from datetime import datetime
from time import sleep
import sys


# PIDs supported by my car (minus the ones I don't need)
SEAT_PIDs = [
    '0101',  # DTC Status (bit-encode)
    '0103',  # Fuel SysStatus (bit-encode)
    '0104',  # Engine load
    '0105',  # Coolant temp
    #0106',  # Short term fuel trim - Bank 1
    #0107',  # Long term fuel trim - Bank 1
    '010B',  # Intake MAP
    '010C',  # RPM
    '010D',  # Speed
    #010E',  # Timing advance
    '010F',  # Intake Air temp
    '0111',  # Throttle position
    #0113',  # O2 sensors present (bit-encode)
    #0115',  # O2 sensor 2 (A=Voltage, B=Short term fuel trim)
    #011C',  # OBD standard
    #0120',  # PIDs supported [21 - 40] (bit-encode)
    #0121',  # Distance traveled with MIL on
    '0134'   # O2 sensor 1 (Fuel-Air eq, Current)
]


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


def debug_log(msg):
    eprint('{} | {}'.format(now(), msg))


def fail_log(msg):
    print('{} | {}'.format(now(), msg))
    debug_log(msg)


def get_data(t, command):
    """
    :param telnetlib.Telnet t:
    :param str command:
    :return:
    """
    eprint('{} : Sending comand: {}'.format(now(), command))
    t.write(command + '\r')
    data = ''
    while '>' not in data:
        data = data + t.read_eager()

    data = data.replace('\r', '|').strip()
    eprint('{} : Received: {}'.format(now(), data))
    print('{}|{}'.format(now(), data))
    return data


def get_arr_data(t, commands):
    """
    :param telnetlib.Telnet t:
    :param list of str command:
    :return:
    """
    o = {}
    for command in commands:
        o[command] = get_data(t, command)
    return o


if __name__ == "__main__":
    debug_log("Initializing Telnet Client ...")
    t = telnetlib.Telnet()

    debug_log("Opening connection ...")
    try:
        t.open(host='192.168.0.10', port=35000, timeout=10)

        debug_log("Connection established, awaiting response ...")
        t.write('\r')
        t.read_until('>')

        debug_log("Initializing environment ...")
        get_data(t, 'ATZ')          # Reset Everything
        get_data(t, 'ATS0')         # Do not print spaces
        get_data(t, 'AT@1')         # Get Device Description
        init = get_data(t, 'ATSI')  # Request supported PIDs to establish vehicle connection

        # If BUS INIT failed, cancel here (restart app and try again)
        if 'BUS INIT:' in init and 'ERROR' in init:
            print('Failed to connect to device')
            debug_log('Failed to connect to device')
            exit(1)

        # Request supported PIDs
        get_data(t, '0100')
        get_data(t, '0120')
        get_data(t, '0140')
        get_data(t, '0160')
        get_data(t, '0180')

        # Request used OBD protocol
        get_data(t, '011C')

        eprint("Connected and ready, starting recording loop")
        request_PIDs = ['ATRV']
        request_PIDs.extend(SEAT_PIDs)
        while True:
            get_arr_data(t, request_PIDs)
    except socket.timeout:
        fail_log("Connection failed! (Timeout on connect)")
        exit(1)
    except KeyboardInterrupt:
        debug_log("Terminated by user")
        exit(0)
