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
from os import path
from sys import exit
from time import sleep

from CarPiConfig import init_config_env
from CarPiLogging import EXIT_CODES, boot_print, end_print, log, print_unhandled_exception
from RedisUtils import get_redis

APP_NAME = path.basename(__file__)

if __name__ == "__main__":
    EXIT_CODE = EXIT_CODES['OK']

    CONFIG = init_config_env('CARPI_NETD_CONF', ['net-daemon.conf', '/etc/carpi/net-daemon.conf'])
    boot_print(APP_NAME)

    CONFIG_DATAPOLLER_INTERVAL = CONFIG.getfloat('DataPoller', 'interval') / 1000

    log("Initializing Redis Connection ...")
    R = get_redis(CONFIG)

    try:
        log("MPD Data & Control Daemon is running ...")
        while True:
            pass
            sleep(CONFIG_DATAPOLLER_INTERVAL)
    except (KeyboardInterrupt, SystemExit):
        log("Shutdown requested!")
    except:
        EXIT_CODE = EXIT_CODES['UnhandledException']
        print_unhandled_exception()
    finally:
        pass

    end_print()
    exit(EXIT_CODE)
