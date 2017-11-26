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

from CarPiLogging import log, boot_print, end_print, print_unhandled_exception, EXIT_CODES
from CarPiConfig import init_config_env
from CarPiUIApp import CarPiUIApp
from PygameUtils import init_io, init_pygame, \
    UI_CONFIG_SECTION, UI_CONFIG_KEY_RES_WIDTH, UI_CONFIG_KEY_RES_HEIGHT, UI_CONFIG_KEY_FULLSCREEN
from RedisUtils import get_redis, get_persistent_redis
from os import path
from sys import exit

APP_NAME = path.basename(__file__)

EXIT_CODE = EXIT_CODES['OK']

if __name__ == "__main__":
    APP = None  # type: CarPiUIApp
    try:
        CONFIG = init_config_env('CARPI_UI_CONFIG', ['ui.conf', '/etc/carpi/ui.conf'])
        boot_print(APP_NAME)

        log("Initializing Data Source ...")
        R = get_redis(CONFIG)
        RP = get_persistent_redis(CONFIG)

        log("Configuring UI ...")
        init_io(CONFIG)
        init_pygame(CONFIG)

        APP = CarPiUIApp(rect=(CONFIG.getint(UI_CONFIG_SECTION, UI_CONFIG_KEY_RES_WIDTH),
                               CONFIG.getint(UI_CONFIG_SECTION, UI_CONFIG_KEY_RES_HEIGHT) - 21),
                         redis=R,
                         pers_redis=RP,
                         title='CarPi',
                         fullscreen=CONFIG.getboolean(UI_CONFIG_SECTION, UI_CONFIG_KEY_FULLSCREEN))
        APP.run()
    except (KeyboardInterrupt, SystemExit):
        log("Shutdown requested")
    except:
        EXIT_CODE = EXIT_CODES['UnhandledException']
        print_unhandled_exception()
    finally:
        log("Shutting down UI ...")
        if APP:
            APP.shutdown()

    end_print(APP_NAME)
    exit(EXIT_CODE)
