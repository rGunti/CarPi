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
import threading
from math import floor
from os import system
from threading import Thread

from CarPiLogging import log
from CarPiStyles import PATH_FONT_VCR, PATH_FONT_DEFAULT
from RedisKeys import NetworkInfoRedisKeys, PersistentGpsRedisKeys
from RedisUtils import RedisBackgroundFetcher, set_piped, save_synced_value, get_piped
from pqGUI import Window, Text, Button, TEXT_FONT, DEFAULT_STYLE, DECO_NONE, BG_COLOR


class CarPiBaseSettingsWindow(Window):
    def __init__(self,
                 parent,
                 title,
                 icon=None,
                 style=None,
                 buttons=DECO_NONE,
                 modal=False):
        Window.__init__(self,
                        parent,
                        ((0, 21), (320, 220)),
                        title,
                        icon=icon,
                        style=style,
                        buttons=buttons,
                        modal=modal)
        self.restrict_position = True
        self._init_controls()

    def _init_controls(self):
        raise NotImplementedError

    def _init_options(self, parent, items=[]):
        for (i, item) in enumerate(items):
            if item is None:
                continue
            pos = ((5 if i % 2 == 0 else 162, 5 + (floor(i / 2) * 40)), (152, 32))
            if isinstance(item, Button):
                button = item  # type: Button
                # button.x = pos[0][0]
                # button.y = pos[0][1]
                # button.width = pos[1][0]
                # button.height = pos[1][1]
                button.pack()
            else:
                Button(parent,
                       pos,
                       item[0],
                       command=item[1],
                       style={TEXT_FONT: (DEFAULT_STYLE[TEXT_FONT][0], 20)}).pack()

    def _back_callback(self, e):
        self.destroy()

    def update(self):
        raise NotImplementedError

    def destroy(self):
        super(CarPiBaseSettingsWindow, self).destroy()


class MainSettingsWindow(CarPiBaseSettingsWindow):
    def __init__(self, parent, redis, pers_redis=None):
        self._redis = redis
        self._pers_redis = pers_redis
        CarPiBaseSettingsWindow.__init__(self, parent, 'Settings')

    def _init_controls(self):
        self._init_options(self, [
            None,
            None,
            ('GPS & Trip', self._gps_settings_button_command),
            ('Network', self._network_settings_button_command),
            ('Display', self._display_settings_button_command),
            ('Power', self._power_settings_button_command),
            None,
            None,
            ('< Back', self._back_callback),
            None
        ])

    def update(self):
        pass

    def _gps_settings_button_command(self, e):
        GpsTripSettingsWindow(self, self._redis, self._pers_redis).show()

    def _network_settings_button_command(self, e):
        NetworkSettingsWindow(self, self._redis).show()

    def _display_settings_button_command(self, e):
        DisplaySettingsWindow(self).show()

    def _power_settings_button_command(self, e):
        PowerSettingsWindow(self).show()


class GpsTripSettingsWindow(CarPiBaseSettingsWindow):
    def __init__(self, parent, temp_redis, persist_redis):
        self._temp_redis = temp_redis
        self._persist_redis = persist_redis

        self._fetcher = RedisBackgroundFetcher(persist_redis, [
            PersistentGpsRedisKeys.KEY_TRIP_A,
            PersistentGpsRedisKeys.KEY_TRIP_B,
            PersistentGpsRedisKeys.KEY_ODO
        ], fetch_interval=1)

        self._trip_a_text = None  # type: Text
        self._trip_b_text = None  # type: Text
        self._odo_text = None  # type: Text

        CarPiBaseSettingsWindow.__init__(self,
                                         parent,
                                         'GPS & Trip Settings')

    def _init_controls(self):
        rec_trip = get_piped(self._persist_redis,
                             [PersistentGpsRedisKeys.KEY_TRIP_A_RECORDING])

        self._init_options(self, [
            ('Reset Trip A', self._reset_trip_a_callback),
            None,
            ('Reset Trip B', self._reset_trip_b_callback),
            None,
            ('ODO Correction', self._correct_odo_callback),
            None,
            ('Start New Trip', self._new_trip_callback),
            ('Stop Recording', self._stop_recording_callback) if PersistentGpsRedisKeys in rec_trip else None,
            ('< Back', self._back_callback),
            None
        ])

        self._trip_a_text = Text(self, ((165, 10), (152, 32)), '', style={TEXT_FONT: (PATH_FONT_VCR, 20)}).pack()
        self._trip_b_text = Text(self, ((165, 50), (152, 32)), '', style={TEXT_FONT: (PATH_FONT_VCR, 20)}).pack()
        self._odo_text = Text(self, ((165, 90), (152, 32)), '', style={TEXT_FONT: (PATH_FONT_VCR, 20)}).pack()

        self._set_distance(self._trip_a_text, 0)
        self._set_distance(self._trip_b_text, 0)
        self._set_distance(self._odo_text, 0)

        self._fetcher.start()

    def _empty_callback(self, e):
        pass

    def update(self):
        new_data = self._fetcher.get_current_data()

        self._set_distance(self._trip_a_text, float(new_data.get(PersistentGpsRedisKeys.KEY_TRIP_A, '0')))
        self._set_distance(self._trip_b_text, float(new_data.get(PersistentGpsRedisKeys.KEY_TRIP_B, '0')))
        self._set_distance(self._odo_text, float(new_data.get(PersistentGpsRedisKeys.KEY_ODO, '0')))

    def _set_distance(self, label, value):
        label.settext('{:>9.2f} km'.format(value / 1000))

    def destroy(self):
        self._fetcher.stop_safe()
        super(GpsTripSettingsWindow, self).destroy()

    def _reset_trip_a_callback(self, e):
        set_piped(self._persist_redis, {PersistentGpsRedisKeys.KEY_TRIP_A: 0})

    def _reset_trip_b_callback(self, e):
        set_piped(self._persist_redis, {PersistentGpsRedisKeys.KEY_TRIP_B: 0})

    def _correct_odo_callback(self, e):
        OdoCorrectionWindow(self, self._persist_redis).show()

    def _new_trip_callback(self, e):
        save_synced_value(self._temp_redis, self._persist_redis, PersistentGpsRedisKeys.KEY_TRIP_A_RECORDING, '999999')
        self._reset_trip_a_callback(e)

    def _stop_recording_callback(self, e):
        save_synced_value(self._temp_redis, self._persist_redis, PersistentGpsRedisKeys.KEY_TRIP_A_RECORDING, None)


class NetworkSettingsWindow(CarPiBaseSettingsWindow):
    def __init__(self, parent, redis):
        self._redis = redis
        self._fetcher = RedisBackgroundFetcher(redis, [
            NetworkInfoRedisKeys.KEY_ETH0_IP,
            NetworkInfoRedisKeys.KEY_WLAN0_STRENGTH,
            NetworkInfoRedisKeys.KEY_WLAN0_SSID,
            NetworkInfoRedisKeys.KEY_WLAN0_IP,
            NetworkInfoRedisKeys.KEY_WLAN1_STRENGTH,
            NetworkInfoRedisKeys.KEY_WLAN1_SSID,
            NetworkInfoRedisKeys.KEY_WLAN1_IP
        ], fetch_interval=5)

        self._ethernet_ip = None  # type: Text
        self._wifi0_ip = None  # type: Text
        self._wifi1_ip = None  # type: Text

        CarPiBaseSettingsWindow.__init__(self, parent, 'Network Settings')

    def _init_controls(self):
        style = {
            TEXT_FONT: (DEFAULT_STYLE[TEXT_FONT][0], 14)
        }

        Text(self, ((10, 10), (300, 25)), 'Ethernet IP:', style=style).pack()
        Text(self, ((10, 35), (300, 25)), 'Hotspot IP:', style=style).pack()
        Text(self, ((10, 60), (300, 25)), 'External IP:', style=style).pack()

        self._ethernet_ip = Text(self, ((100, 10), (190, 25)), '...', style=style).pack()
        self._wifi0_ip = Text(self, ((100, 35), (190, 25)), '...', style=style).pack()
        self._wifi1_ip = Text(self, ((100, 60), (190, 25)), '...', style=style).pack()

        self._init_options(self, [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            ('< Back', self._back_callback),
            None
        ])

        self._fetcher.start()

    def update(self):
        new_data = self._fetcher.get_current_data()
        self._ethernet_ip.settext(new_data.get(NetworkInfoRedisKeys.KEY_ETH0_IP, '-'))
        self._wifi0_ip.settext(new_data.get(NetworkInfoRedisKeys.KEY_WLAN0_IP, '-'))
        self._wifi1_ip.settext(new_data.get(NetworkInfoRedisKeys.KEY_WLAN1_IP, '-'))

    def destroy(self):
        self._fetcher.stop()
        super(NetworkSettingsWindow, self).destroy()


class DisplaySettingsWindow(CarPiBaseSettingsWindow):
    def __init__(self, parent):
        CarPiBaseSettingsWindow.__init__(self, parent, 'Display Settings')

    def _init_controls(self):
        self._init_options(self, [
            None,
            None,
            ('Dark', self._dark_callback),
            ('Bright', self._bright_callback),
            None,
            None,
            None,
            None,
            ('< Back', self._back_callback),
            None
        ])

    def _dark_callback(self, e):
        system('echo 30 > /dev/lcdlevel')

    def _bright_callback(self, e):
        system('echo 100 > /dev/lcdlevel')

    def update(self):
        pass


class PowerSettingsWindow(CarPiBaseSettingsWindow):
    def __init__(self, parent):
        self._maint_button = None  # type: Button
        self._reboot_to_maint = False
        CarPiBaseSettingsWindow.__init__(self, parent, 'Power Settings')

    def _init_controls(self):
        self._maint_button = Button(self,
                                    # formula from _init_options()
                                    ((5 if 9 % 2 == 0 else 162, 5 + (floor(9 / 2) * 40)), (152, 32)),
                                    'Maint. Mode',
                                    style={TEXT_FONT: (DEFAULT_STYLE[TEXT_FONT][0], 20)},
                                    command=self._reboot_maint_callback)
        self._init_options(self, [
            None,
            None,
            ('Power Off', self._shutdown_callback),
            ('Reboot', self._reboot_callback),
            None,
            None,
            None,
            ('Exit', self._exit_callback),
            ('< Back', self._back_callback),
            self._maint_button
        ])

    def _shutdown_callback(self, e):
        PowerSettingsRunningWindow(self,
                                   'Shutting down...',
                                   'Please wait a moment...',
                                   threading.Timer(3, self.on_shutdown)).show()

    def _reboot_callback(self, e):
        PowerSettingsRunningWindow(self,
                                   'Rebooting...',
                                   'Please wait a moment...',
                                   threading.Timer(3, self.on_reboot)).show()

    def _reboot_maint_callback(self, e):
        self._reboot_to_maint = not self._reboot_to_maint

    def _exit_callback(self, e):
        self.on_exit()
        #PowerSettingsRunningWindow(self,
        #                           'Exiting...',
        #                           'Please wait a moment...',
        #                           threading.Timer(3, self.on_exit)).show()

    def on_shutdown(self):
        system('shutdown -P now')

    def on_reboot(self):
        if self._reboot_to_maint:
            with open('/boot/start_maint', 'w') as f:
                f.write('BOOT INTO MAINT MODE')
        system('shutdown -r now')

    def on_exit(self):
        exit(0)
        raise KeyboardInterrupt

    def update(self):
        self._maint_button.style[BG_COLOR] = (219, 164, 0) if self._reboot_to_maint \
            else (0, 0, 0)


class PowerSettingsRunningWindow(CarPiBaseSettingsWindow):
    def __init__(self, parent, title, message, timer_object):
        """
        :param parent:
        :param title:
        :param message:
        :param threading.Timer timer_object:
        """
        self._thread = timer_object
        timer_object.start()
        CarPiBaseSettingsWindow.__init__(self, parent, title)
        self._processing_text = Text(self,
                                     ((10, 75), (300, 75)),
                                     message,
                                     style={TEXT_FONT: (DEFAULT_STYLE[TEXT_FONT][0], 20)}).pack()

    def _init_controls(self):
        pass

    def update(self):
        pass


class OdoCorrectionWindow(CarPiBaseSettingsWindow):
    def __init__(self, parent, redis):
        self._redis = redis

        self._output = None  # type: Text
        self._value = ''

        CarPiBaseSettingsWindow.__init__(self, parent, 'ODO Correction')

    def _init_controls(self):
        self._output = Text(self, ((85, 5), (160, 32)), '------.--- km', style={TEXT_FONT: (PATH_FONT_VCR, 20)}).pack()

        Button(self, ((5,   40), (100, 40)), '7', style={TEXT_FONT: (PATH_FONT_VCR, 20)}, command=self._get_numpad_command(7)).pack()
        Button(self, ((110, 40), (100, 40)), '8', style={TEXT_FONT: (PATH_FONT_VCR, 20)}, command=self._get_numpad_command(8)).pack()
        Button(self, ((215, 40), (100, 40)), '9', style={TEXT_FONT: (PATH_FONT_VCR, 20)}, command=self._get_numpad_command(9)).pack()

        Button(self, ((5,   85), (100, 40)), '4', style={TEXT_FONT: (PATH_FONT_VCR, 20)}, command=self._get_numpad_command(4)).pack()
        Button(self, ((110, 85), (100, 40)), '5', style={TEXT_FONT: (PATH_FONT_VCR, 20)}, command=self._get_numpad_command(5)).pack()
        Button(self, ((215, 85), (100, 40)), '6', style={TEXT_FONT: (PATH_FONT_VCR, 20)}, command=self._get_numpad_command(6)).pack()

        Button(self, ((5,   130), (100, 40)), '1', style={TEXT_FONT: (PATH_FONT_VCR, 20)}, command=self._get_numpad_command(1)).pack()
        Button(self, ((110, 130), (100, 40)), '2', style={TEXT_FONT: (PATH_FONT_VCR, 20)}, command=self._get_numpad_command(2)).pack()
        Button(self, ((215, 130), (100, 40)), '3', style={TEXT_FONT: (PATH_FONT_VCR, 20)}, command=self._get_numpad_command(3)).pack()

        Button(self, ((5,   175), (100, 40)), '<', style={TEXT_FONT: (PATH_FONT_VCR, 20)}, command=self._delete_character).pack()
        Button(self, ((110, 175), (100, 40)), '0', style={TEXT_FONT: (PATH_FONT_VCR, 20)}, command=self._get_numpad_command(0)).pack()
        Button(self, ((215, 175), (50, 40)), 'OK', style={TEXT_FONT: (PATH_FONT_DEFAULT, 20), BG_COLOR: (0, 100, 0)}, command=self._ok_command).pack()
        Button(self, ((270, 175), (45, 40)), 'X', style={TEXT_FONT: (PATH_FONT_DEFAULT, 20), BG_COLOR: (100, 0, 0)}, command=self._back_callback).pack()

    def update(self):
        pass

    def _get_numpad_command(self, num):
        def _numpad_function(e):
            if len(self._value) >= 9 or (len(self._value) == 0 and num == 0):
                return
            self._value = self._value + str(num)
            self._set_distance(self._value)

        return _numpad_function

    def _delete_character(self, e):
        if len(self._value) > 0:
            self._value = self._value[0:len(self._value) - 1]
            self._set_distance(self._value)

    def _set_distance(self, value):
        try:
            self._output.settext('{:->10.3f} km'.format(float(value) / 1000))
        except ValueError:
            self._output.settext('------.--- km')

    def _ok_command(self, e):
        try:
            value = float(self._value)
            set_piped(self._redis, {PersistentGpsRedisKeys.KEY_ODO: value})
        except ValueError:
            pass
        finally:
            self.destroy()


if __name__ == "__main__":
    print("This script is not intended to be run standalone!")
