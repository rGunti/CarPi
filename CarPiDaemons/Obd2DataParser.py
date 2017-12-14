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
from CarPiLogging import log
from RedisKeys import ObdRedisKeys


class ObdPidParserUnknownError(Exception):
    def __init__(self, type, val=None):
        """
        :param str type: OBD PID
        :param str val: (optional) value received to parse
        """
        log("Unknown or unimplemented OBD PID {} (Value was: {})".format(type, val))
        self.type = type
        self.val = val


def trim_obd_value(v):
    """
    Trims unneeded data from an OBD response
    :param str v:
    :return str:
    """
    if not v or len(v) < 4:
        return ''
    else:
        return v[4:]


def prepare_value(v):
    """
    :param str v:
    :return str:
    """
    a = v.split('|')
    if len(a) >= 2 and a[1] != '>':
        return a[1]
    else:
        return None


def parse_value(type, val):
    """
    Parses a given OBD value of a given type (PID)
    and returns the parsed value.
    If the PID is unknown / not implemented a PIDParserUnknownError
    will be raised including the type which was unknown
    :param type:
    :param val:
    :return:
    """
    if type in PARSER_MAP:
        return PARSER_MAP[type](prepare_value(val))
    else:
        raise ObdPidParserUnknownError(type, val)


def parse_obj(o):
    """
    Parses a given dictionary with the key being the OBD PID and the value its
    returned value by the OBD interface
    :param dict o:
    :return:
    """
    r = {}
    for k, v in o.items():
        r[k] = parse_value(k, v)
    return o


def transform_obj(o):
    r = {}
    for k, v in o.items():
        if v is tuple:
            keys = OBD_REDIS_MAP[k]
            r[keys[0]] = v[0]
            r[keys[1]] = v[1]
        else:
            r[OBD_REDIS_MAP[k]] = v
    r[ObdRedisKeys.KEY_ALIVE] = 1
    return r


def parse_atrv(v):
    """
    Parses the battery voltage and returns it in [Volt] as float with 1 decimal place
    :param str v: e.g. "12.3V"
    :return float:
    """
    try:
        return float(v.replace('V', ''))
    except ValueError:
        return float('nan')


def parse_0104(v):
    """
    Parses the calculated engine load and returns it as an integer from 0 - 100
    :param str v: e.g. "410405"
    :return int: e.g. 2
    """
    try:
        val = int(trim_obd_value(v), 16)
        return val / 2.55
    except ValueError:
        return float('nan')


def parse_010B(v):
    """
    Parses Intake MAP and returns it in [kPa] as an integer from 0 - 255
    :param str v:
    :return int:
    """
    try:
        return int(trim_obd_value(v), 16)
    except ValueError:
        return float('nan')


def parse_010C(v):
    """
    Parses Engine RPM and returns it in [RPM] as a float from 0 - 16383.75
    :param str v:
    :return float:
    """
    try:
        val = int(trim_obd_value(v), 16)
        return val / 4
    except ValueError:
        return float('nan')


def parse_010D(v):
    """
    Parses Vehicle Speed and returns it in [km/h] as an integer from 0 - 255
    :param str v:
    :return int:
    """
    try:
        return int(trim_obd_value(v), 16)
    except ValueError:
        return float('nan')


def parse_010F(v):
    """
    Parses Intake Air Temperature and returns it in [degrees C] as an integer from -40 - 215
    :param str v:
    :return int:
    """
    try:
        val = int(trim_obd_value(v), 16)
        return val - 40
    except ValueError:
        return float('nan')


def parse_0134_013B(v):
    """
    Parses the O2 Sensor Value (0134 - 013B) and returns two values parsed from it:
    1. Fuel-Air Equivalence [Ratio] as a float from 0 - 2
    2. Current in [mA] as a float from -128 - 128
    :param str v:
    :return tuple of float, float:
    """
    try:
        trim_val = trim_obd_value(v)
        val_ab = int(trim_val[0:2], 16)
        val_cd = int(trim_val[2:4], 16)
        return (2 / 65536) * val_ab, val_cd - 128
    except ValueError:
        return float('nan'), float('nan')


PARSER_MAP = {
    'ATRV': parse_atrv,
    '0104': parse_0104,
    '0105': parse_010F,
    '010B': parse_010B,
    '010C': parse_010C,
    '010D': parse_010D,
    '010F': parse_010F,
    '0134': parse_0134_013B,
    '0135': parse_0134_013B,
    '0136': parse_0134_013B,
    '0137': parse_0134_013B,
    '0138': parse_0134_013B,
    '0139': parse_0134_013B,
    '013A': parse_0134_013B,
    '013B': parse_0134_013B
}

OBD_REDIS_MAP = {
    'ATRV': ObdRedisKeys.KEY_BATTERY_VOLTAGE,
    '0104': ObdRedisKeys.KEY_ENGINE_LOAD,
    '0105': ObdRedisKeys.KEY_COOLANT_TEMP,
    '010B': ObdRedisKeys.KEY_INTAKE_MAP,
    '010C': ObdRedisKeys.KEY_ENGINE_RPM,
    '010D': ObdRedisKeys.KEY_VEHICLE_SPEED,
    '010F': ObdRedisKeys.KEY_INTAKE_TEMP,
    '0134': (ObdRedisKeys.KEY_O2_SENSOR_FAEQV, ObdRedisKeys.KEY_O2_SENSOR_CURRENT),
    '0135': (ObdRedisKeys.KEY_O2_SENSOR_FAEQV, ObdRedisKeys.KEY_O2_SENSOR_CURRENT),
    '0136': (ObdRedisKeys.KEY_O2_SENSOR_FAEQV, ObdRedisKeys.KEY_O2_SENSOR_CURRENT),
    '0137': (ObdRedisKeys.KEY_O2_SENSOR_FAEQV, ObdRedisKeys.KEY_O2_SENSOR_CURRENT),
    '0138': (ObdRedisKeys.KEY_O2_SENSOR_FAEQV, ObdRedisKeys.KEY_O2_SENSOR_CURRENT),
    '0139': (ObdRedisKeys.KEY_O2_SENSOR_FAEQV, ObdRedisKeys.KEY_O2_SENSOR_CURRENT),
    '013A': (ObdRedisKeys.KEY_O2_SENSOR_FAEQV, ObdRedisKeys.KEY_O2_SENSOR_CURRENT),
    '013B': (ObdRedisKeys.KEY_O2_SENSOR_FAEQV, ObdRedisKeys.KEY_O2_SENSOR_CURRENT)
}

if __name__ == "__main__":
    print("This script is not intended to be run standalone!")
