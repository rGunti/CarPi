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

from threading import Thread
from time import sleep
from CarPiLogging import log


class ThreadStopTimeoutError(Exception):
    pass


class CarPiThread(Thread):
    def __init__(self, interval=None):
        Thread.__init__(self)
        self._interval = interval
        self._running = True

    def run(self):
        log("{} has started".format(self.__class__.__name__))
        while self._running:
            self._do()
            if self._interval:
                sleep(self._interval)

    def _do(self):
        raise NotImplementedError

    def stop(self, timeout=5):
        log("Stopping {} ...".format(self.__class__.__name__))
        self._running = False
        self.join(timeout)
        if self.isAlive():
            raise ThreadStopTimeoutError

    def stop_safe(self, timeout=5):
        try:
            self.stop(timeout)
            return True
        except ThreadStopTimeoutError:
            log("Stopping {} timed out after {} seconds!".format(
                self.__class__.__name__, timeout))
            return False


if __name__ == "__main__":
    print("This script is not intended to be run standalone!")
