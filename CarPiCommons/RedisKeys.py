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

    KEY_LOCATION_COUNTRY = 'GPS.Location.Country'  # type: str
    KEY_LOCATION_CITY = 'GPS.Location.City'  # type: str
    KEY_LOCATION_ADMIN1 = 'GPS.Location.Admin1'  # type: str
    KEY_LOCATION_ADMIN2 = 'GPS.Location.Admin2'  # type: str

    KEY_TRIP_A_RECORDING = 'Trip.A.ID'

    KEY_ALIVE = 'DaemonAlive.GPS'  # type: str

    KEYS = [
        KEY_ALIVE,
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


class PersistentGpsRedisKeys:
    KEY_ODO = 'GPS.ODO'
    KEY_TRIP_A = 'GPS.Trip.A'
    KEY_TRIP_B = 'GPS.Trip.B'

    KEY_TRIP_A_RECORDING = 'Trip.A.ID'

    KEYS = [
        KEY_ODO,
        KEY_TRIP_A,
        KEY_TRIP_B,
        KEY_TRIP_A_RECORDING
    ]


class NetworkInfoRedisKeys:
    KEY_ETH0_IP = 'Net.eth0.IP'  # type: str
    KEY_WLAN0_IP = 'Net.wlan0.IP'  # type: str
    KEY_WLAN0_STRENGTH = 'Net.wlan0.Strength'  # type: str
    KEY_WLAN0_SSID = 'Net.wlan0.SSID'  # type: str
    KEY_WLAN1_IP = 'Net.wlan1.IP'  # type: str
    KEY_WLAN1_STRENGTH = 'Net.wlan1.Strength'  # type: str
    KEY_WLAN1_SSID = 'Net.wlan1.SSID'  # type: str

    KEY_ALIVE = 'DaemonAlive.Net'  # type: str

    KEYS = [
        KEY_ALIVE,
        KEY_ETH0_IP,
        KEY_WLAN0_IP,
        KEY_WLAN0_STRENGTH,
        KEY_WLAN0_SSID,
        KEY_WLAN1_IP,
        KEY_WLAN1_STRENGTH,
        KEY_WLAN1_SSID
    ]


class MpdDataRedisKeys:
    KEY_STATE = 'MPD.State'  # type: str
    KEY_SONG_TITLE = 'MPD.CurrentSong.Title'  # type: str
    KEY_SONG_ARTIST = 'MPD.CurrentSong.Artist'  # type: str
    KEY_SONG_ALBUM = 'MPD.CurrentSong.Album'  # type: str
    KEY_SONG_LENGTH = 'MPD.CurrentSong.Length'  # type: str
    KEY_SONG_LENGTH_FORMATTED = 'MPD.CurrentSong.Length.Formatted'  # type: str
    KEY_CURRENT_TIME = 'MPD.CurrentTime'  # type: str
    KEY_CURRENT_TIME_FORMATTED = 'MPD.CurrentTime.Formatted'  # type: str
    KEY_VOLUME = 'MPD.Volume'  # type: str
    KEY_RANDOM = 'MPD.Random'  # type: str
    KEY_REPEAT = 'MPD.Repeat'  # type: str

    KEY_ALIVE = 'DaemonAlive.MPD'  # type: str

    KEYS = [
        KEY_ALIVE,
        KEY_SONG_TITLE,
        KEY_SONG_ARTIST,
        KEY_SONG_ALBUM,
        KEY_CURRENT_TIME,
        KEY_CURRENT_TIME_FORMATTED,
        KEY_VOLUME
    ]


class MpdCommandRedisKeys:
    KEY_ALIVE = MpdDataRedisKeys.KEY_ALIVE

    # Commands
    COMMAND_PLAY = 'CommandRequest(MPD.Play)'
    COMMAND_PAUSE = 'CommandRequest(MPD.Pause)'
    COMMAND_STOP = 'CommandRequest(MPD.Stop)'
    COMMAND_NEXT = 'CommandRequest(MPD.Next)'
    COMMAND_PREV = 'CommandRequest(MPD.Prev)'

    # Parameters
    # COMMAND_PAUSE
    PARAM_PAUSE_VALUE = 'PauseValue'

    COMMANDS = [
        COMMAND_PLAY,
        COMMAND_PAUSE,
        COMMAND_STOP,
        COMMAND_NEXT,
        COMMAND_PREV
    ]
    PARAMS = {
        # COMMAND_PLAY: [],
        COMMAND_PAUSE: [ PARAM_PAUSE_VALUE ],
        # COMMAND_STOP: []
    }


class ObdRedisKeys:
    KEY_ALIVE = 'OBD.State'

    KEY_BATTERY_VOLTAGE = 'OBD.BatteryVoltage'
    KEY_ENGINE_LOAD = 'OBD.EngineLoad'
    KEY_COOLANT_TEMP = 'OBD.CoolantTemp'
    KEY_INTAKE_MAP = 'OBD.IntakeMAP'
    KEY_ENGINE_RPM = 'OBD.RPM'
    KEY_VEHICLE_SPEED = 'OBD.Speed'
    KEY_INTAKE_TEMP = 'OBD.IntakeTemp'
    KEY_O2_SENSOR_FAEQV = 'OBD.O2Sensor.FuelAirEqRatio'
    KEY_O2_SENSOR_CURRENT = 'OBD.O2Sensor.Current'
    KEY_FUELSYS_1_STATUS = 'OBD.FuelSystem1.Status'
    KEY_FUELSYS_2_STATUS = 'OBD.FuelSystem2.Status'
    KEY_MIL_STATUS = 'OBD.MIL'
    KEY_DTC_COUNT = 'OBD.DTCCount'

    KEYS = [
        KEY_ALIVE,
        KEY_BATTERY_VOLTAGE,
        KEY_ENGINE_LOAD,
        KEY_INTAKE_MAP,
        KEY_ENGINE_RPM,
        KEY_VEHICLE_SPEED,
        KEY_INTAKE_TEMP,
        KEY_O2_SENSOR_FAEQV,
        KEY_O2_SENSOR_CURRENT
    ]


def prepare_dict(keys, default_value=None):
    dict = {}
    for key in keys:
        dict[key] = default_value
    return dict


if __name__ == "__main__":
    print("This script is not intended to be run standalone!")
