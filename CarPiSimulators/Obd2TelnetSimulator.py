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


DATA = {
    'PING': 'PONG',
    'AT@1': 'OBD2 Telnet Simulator Server',
    'ATRV': '12.7V',
    '0100': '00000000',  # 4 bytes: PID Support 01-20, bit encoded
    '0101': '00000000',  # 4 bytes: Bit A7 => MIL, A6-A0 => Num. of DTCs
#   '0102': '',
    '0103': '0000',      # 2 bytes: Fuel System #1 / #2 Status, bit encoded
    '0104': '00',        # 1 byte : Engine Load (0 - 255)              [val% = A / 255]
    '0105': '00',        # 1 byte : Engine coolant temp (-40 - 215)    [val = A - 40]
#   '0106' - '0109',
    '010A': '00',        # 1 byte : Fuel Pressure (kPa, 0 - 765)       [val = 3 * A]
    '010B': '00',        # 1 byte : Intake MAP in kPa (0 - 255)        [val = A]
    '010C': '0000',      # 2 bytes: Engine RPM (0 - 16383.75)          [val = (256A + B) / 4]
    '010D': '00',        # 1 byte : Vehicle Speed in km/h (0 - 255)    [val = A]
#   '010E': '',
    '010F': '00',        # 1 byte : Intake air temp (-40 - 215)        [val = A - 40]
    '0110': '0000',      # 2 bytes: MAF air flow rate g/s (0 - 655.35) [val = (256A + B) / 100]
    '0111': '00',        # 1 byte : Throttle position (0 - 255)        [val% = A / 255]
#   '0112' - '011B',
    '011C': '07',        # 1 byte : OBD standard of vehicle, bit encoded
#   '011D' - '011E',
    '011F': '0000',      # 2 bytes: Engine runtime in sec.             [val = 256A + B]
    '0120': '00000000',  # 4 bytes: PID Support 21-40, bit encoded
    '0121': '0000',      # 2 bytes: Distance traveled with MIL, km     [val = 256A + B]
#   '0122' - '012E',
    '012F': '00',        # 1 byte : Fuel Tank Level (0 - 255)          [val% = A / 100]
    '0130': '00',        # 1 byte : Warm-ups since DTCs cleared        [val = A]
    '0131': '0000',      # 2 bytes: Distance since DTCs cleared, km    [val = 256A + B]
#   '0132' - '01EE',
    '013F': '00',        # 1 byte : Fuel Tank Level (0 - 255)          [val% = A / 100]
}


class Obd2TelnetSimulator(TelnetHandler):
    PROMPT = ">"
    WELCOME = "\r"

    @command('DEVSET')
    def command_devset(self, params):
        ''' <Command> <Value>
        Set value for given command
        '''
        if len(params) != 2:
            self.writeline('INVALID')
        else:
            key, value = params  # type: str, str
            DATA[key.upper()] = value.upper()
            self.writeline('OK')

    @command('PING')
    def command_echo(self, params):
        '''
        PING command
        '''
        self.writeline(DATA['PING'])

    @command('ATRV')
    def command_at_rv(self, params):
        '''
        Get Voltage
        '''
        self.writeline(DATA['ATRV'])

    @command('AT@1')
    def command_at_1(self, params):
        '''
        Device Identifier
        '''
        self.writeline(DATA['AT@1'])

    @command('01')
    def command_mode01(self, params):
        '''<PID>
        Mode 01 PID <pid>
        '''
        if len(params) != 1 or len(params[0]) != 2:
            self.writeline('NO DATA')
            return
        key = '01' + params[0]
        if key in DATA:
            self.writeline('41' + params[0] + DATA[key])
        else:
            self.writeline('NO DATA')

    @command('AT@2')
    @command('AT@3')
    @command('AT@3')
    @command('ATCV')
    def command_unhandled(self, params):
        '''
        Unsupported Command
        '''
        self.writeline("NO DATA")


class TelnetServer(SocketServer.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    print("Initializing Telnet Server ...")
    server = TelnetServer(('127.0.0.1', 8023),
                          Obd2TelnetSimulator)
    server.serve_forever()
