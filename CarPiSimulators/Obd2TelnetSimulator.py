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
from telnetsrv.threaded import TelnetHandler, command
from time import sleep
import SocketServer


class Obd2TelnetSimulator(TelnetHandler):
    PROMPT = ">"
    WELCOME = ""

    @command('PING')
    def command_echo(self, params):
        sleep(0.15)
        self.writeline('PONG')

    @command('ATRV')
    def command_at_rv(self, params):
        sleep(0.15)
        self.writeline('12.7V')

    @command('@1')
    def command_at_1(self, params):
        sleep(0.15)
        self.writeline("OBD2 Telnet Simulator Server")

    @command('@2')
    def command_at_2(self, params):
        sleep(0.15)
        self.writeline("NO DATA")


class TelnetServer(SocketServer.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    server = TelnetServer(("0.0.0.0", 8023), Obd2TelnetSimulator)
    server.serve_forever()
