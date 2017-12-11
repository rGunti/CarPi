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
import telnetlib
from datetime import datetime
from time import sleep

import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


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
    eprint("{} : Initializing Telnet Client ...".format(now()))
    t = telnetlib.Telnet()

    eprint("{} : Opening connection ...".format(now()))
    # t.open(host='127.0.0.1', port=8023)
    t.open(host='192.168.0.10', port=35000)
    t.write('\r')

    eprint("{} : Awaiting connect ...".format(now()))
    t.read_until('>')

    eprint("{} : Setting up connection ...".format(now()))
    get_data(t, 'ATZ')
    # get_data(t, 'ATR1')
    get_data(t, 'ATS0')
    get_data(t, 'AT@1')
    init = get_data(t, '0100')
    if 'BUS INIT:' in init and 'ERROR' in init:
        print('Failed to connect to device')
        eprint('Failed to connect to device')
        exit(1)

    get_data(t, '0100')
    get_data(t, '0120')
    get_data(t, '0140')
    get_data(t, '0160')
    get_data(t, '0180')
    get_data(t, '011C')

    eprint("{} : Connected and ready".format(now()))
    while True:
        get_arr_data(t, [
            'ATRV',
            '0103',
            '0104',
            '0105',
            '010A',
            '010B',
            '010C',
            '010D',
            '010F',
            '0110',
            '0111',
            '0130',
            '0131'
        ])
        sleep(0.5)

