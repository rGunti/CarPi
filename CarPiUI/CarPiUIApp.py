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
from math import isnan, floor
from redis import Redis
from time import strftime

from CarPiLogging import log
from CarPiSettingsWindows import MainSettingsWindow
from CarPiUtils import get_mpd_status_time
from CarPiStyles import PATH_FONT_7SEGM, PATH_FONT_VCR, PATH_FONT_NORA_MEDIUM, PATH_FONT_DEFAULT
from RedisKeys import GpsRedisKeys, NetworkInfoRedisKeys, MpdDataRedisKeys, MpdCommandRedisKeys, PersistentGpsRedisKeys, \
    ObdRedisKeys
from pqGUI import pqApp, Text, Graph, Image, TEXT_FONT, TEXT_COLOR, Button, TRANS, BG_COLOR, TEXT_DISABLED, Widget, \
    ProgressBar
from PygameUtils import load_image
from RedisUtils import RedisBackgroundFetcher, send_command_request
from os import path

STYLE_TAB_BUTTON = {
    TEXT_COLOR: (128, 128, 128),
    TEXT_DISABLED: (255, 255, 255),
    BG_COLOR: (20, 20, 20)
}

IMG_ETHERNET_OFF = path.join('res', 'img', 'ethernet-off.png')
IMG_ETHERNET = path.join('res', 'img', 'ethernet-ok.png')
IMG_WIFI_OFF = path.join('res', 'img', 'wifi-off.png')
IMG_WIFI0 = path.join('res', 'img', 'wifi0.png')
IMG_WIFI1 = path.join('res', 'img', 'wifi1.png')
IMG_WIFI2 = path.join('res', 'img', 'wifi2.png')
IMG_WIFI3 = path.join('res', 'img', 'wifi3.png')


class CarPiUIApp(pqApp):
    PAGE_GPS = 'GPS'
    PAGE_MUSIC = 'Clock'
    PAGE_SETTINGS = 'Settings'

    def __init__(self,
                 rect,
                 redis,
                 pers_redis,
                 title='CarPi',
                 fullscreen=False):
        log("Initializing CarPiUIApp ...")
        pqApp.__init__(self,
                       rect=rect,
                       title=title,
                       fullscreen=fullscreen)

        # Internal Data Storage & Processing
        self.image_store = {}
        self._pages = {}
        self._redis_pages = {}
        self._predis_pages = {}
        self._current_page = None  # type: str
        self._fetcher = None  # type: RedisBackgroundFetcher
        self._predis_fetcher = None  # type: RedisBackgroundFetcher
        self._redis = redis  # type: Redis
        self._pers_redis = pers_redis  # type: Redis

        # Tabs
        self._gps_tab_button = None  # type: Button
        self._music_tab_button = None  # type: Button
        self._settings_tab_button = None  # type: Button

        # GPS Data
        self._speed_label = None  # type: Text
        self._speed_unit = None  # type: Text
        self._speed_graph = None  # type: Graph
        self._location_label = None  # type: Text

        self._gps_status_icon = None  # type: Image
        self._car_status_icon = None  # type: Image

        # Trip Data
        self._trip_meter = None  # type: Text
        self._odo_meter = None  # type: Text
        self._trip_odo_unit = None  # type: Text

        # Status Bar
        self._ethernet_status_icon = None  # type: Image
        self._wlan0_status_icon = None  # type: Image
        self._wlan1_status_icon = None  # type: Image
        self._time_label = None  # type: Text

        # Music Display
        self._current_title = None  # type: Text
        self._current_artist = None  # type: Text
        self._current_album = None  # type: Text

        # Music Status
        self._current_song_time = None  # type: Text
        self._current_song_time_bar = None  # type: ProgressBar

        # Music Controls
        self._next_song_button = None  # type: Button
        self._prev_song_button = None  # type: Button
        self._play_song_button = None  # type: Button

        # Load Resources
        self._load()

        # Init Controls
        self._init_controls()

        # Define UI Pages
        gps_page = [
            self._speed_label,
            self._speed_graph,
            self._speed_unit,
            self._odo_meter,
            self._trip_meter,
            self._trip_odo_unit,
            self._location_label
        ]
        music_page = [
            self._current_title,
            self._current_artist,
            self._current_album,
            self._current_song_time,
            self._current_song_time_bar,
            self._next_song_button,
            self._prev_song_button,
            self._play_song_button
        ]
        settings_page = []

        self._pages[CarPiUIApp.PAGE_GPS] = gps_page
        self._pages[CarPiUIApp.PAGE_MUSIC] = music_page
        self._pages[CarPiUIApp.PAGE_SETTINGS] = settings_page

        # Define Redis Pages
        gps_r_page = [
            # Alive Keys
            GpsRedisKeys.KEY_ALIVE,
            NetworkInfoRedisKeys.KEY_ALIVE,
            MpdDataRedisKeys.KEY_ALIVE,

            # Always present keys
            NetworkInfoRedisKeys.KEY_ETH0_IP,
            NetworkInfoRedisKeys.KEY_WLAN0_STRENGTH,
            NetworkInfoRedisKeys.KEY_WLAN0_SSID,
            NetworkInfoRedisKeys.KEY_WLAN1_STRENGTH,
            NetworkInfoRedisKeys.KEY_WLAN1_SSID,

            GpsRedisKeys.KEY_SPEED,
            GpsRedisKeys.KEY_SPEED_KMH,
            MpdDataRedisKeys.KEY_STATE,

            # OBD & Fuel Consumption
            ObdRedisKeys.KEY_ALIVE,
            ObdRedisKeys.KEY_ENGINE_RPM,
            ObdRedisKeys.KEY_INTAKE_TEMP,
            ObdRedisKeys.KEY_INTAKE_MAP,
            ObdRedisKeys.KEY_VEHICLE_SPEED,

            # Specific Keys
            GpsRedisKeys.KEY_EPX,
            GpsRedisKeys.KEY_EPY
        ]
        music_r_page = [
            # Alive Keys
            GpsRedisKeys.KEY_ALIVE,
            NetworkInfoRedisKeys.KEY_ALIVE,
            MpdDataRedisKeys.KEY_ALIVE,

            # Always present keys
            NetworkInfoRedisKeys.KEY_ETH0_IP,
            NetworkInfoRedisKeys.KEY_WLAN0_STRENGTH,
            NetworkInfoRedisKeys.KEY_WLAN0_SSID,
            NetworkInfoRedisKeys.KEY_WLAN1_STRENGTH,
            NetworkInfoRedisKeys.KEY_WLAN1_SSID,

            GpsRedisKeys.KEY_SPEED,
            GpsRedisKeys.KEY_SPEED_KMH,
            MpdDataRedisKeys.KEY_STATE,

            # OBD & Fuel Consumption
            ObdRedisKeys.KEY_ALIVE,
            ObdRedisKeys.KEY_ENGINE_RPM,
            ObdRedisKeys.KEY_INTAKE_TEMP,
            ObdRedisKeys.KEY_INTAKE_MAP,
            ObdRedisKeys.KEY_VEHICLE_SPEED,

            # Specific Keys
            MpdDataRedisKeys.KEY_SONG_TITLE,
            MpdDataRedisKeys.KEY_SONG_ARTIST,
            MpdDataRedisKeys.KEY_SONG_ALBUM,
            MpdDataRedisKeys.KEY_CURRENT_TIME,
            MpdDataRedisKeys.KEY_CURRENT_TIME_FORMATTED
        ]
        settings_r_page = [
            # Alive Keys
            GpsRedisKeys.KEY_ALIVE,
            NetworkInfoRedisKeys.KEY_ALIVE,
            MpdDataRedisKeys.KEY_ALIVE,

            # Always present keys
            NetworkInfoRedisKeys.KEY_ETH0_IP,
            NetworkInfoRedisKeys.KEY_WLAN0_STRENGTH,
            NetworkInfoRedisKeys.KEY_WLAN0_SSID,
            NetworkInfoRedisKeys.KEY_WLAN1_STRENGTH,
            NetworkInfoRedisKeys.KEY_WLAN1_SSID,

            GpsRedisKeys.KEY_SPEED_KMH,
            MpdDataRedisKeys.KEY_STATE,

            # OBD & Fuel Consumption
            ObdRedisKeys.KEY_ALIVE,
            ObdRedisKeys.KEY_ENGINE_RPM,
            ObdRedisKeys.KEY_INTAKE_TEMP,
            ObdRedisKeys.KEY_INTAKE_MAP,
            ObdRedisKeys.KEY_VEHICLE_SPEED,

            # Specific Keys
        ]

        self._redis_pages[CarPiUIApp.PAGE_GPS] = gps_r_page
        self._redis_pages[CarPiUIApp.PAGE_MUSIC] = music_r_page
        self._redis_pages[CarPiUIApp.PAGE_SETTINGS] = settings_r_page

        # Define Persistent Redis Pages
        self._predis_pages[CarPiUIApp.PAGE_GPS] = PersistentGpsRedisKeys.KEYS
        self._predis_pages[CarPiUIApp.PAGE_MUSIC] = []
        self._predis_pages[CarPiUIApp.PAGE_SETTINGS] = []

    def _load(self):
        self.load_image(IMG_ETHERNET_OFF)
        self.load_image(IMG_ETHERNET)
        self.load_image(IMG_WIFI_OFF)
        self.load_image(IMG_WIFI0)
        self.load_image(IMG_WIFI1)
        self.load_image(IMG_WIFI2)
        self.load_image(IMG_WIFI3)

        self._fetcher = RedisBackgroundFetcher(self._redis, [])
        self._predis_fetcher = RedisBackgroundFetcher(self._pers_redis, [])

    def load_image(self, image_path):
        if image_path not in self.image_store:
            self.image_store[image_path] = load_image(image_path)
        else:
            log("Image \"{}\" already loaded".format(image_path))

    def get_image(self, image_path):
        if image_path not in self.image_store:
            log("Image \"{}\" not loaded! Load image before use!".format(image_path))
            return None
        else:
            return self.image_store[image_path]

    def _init_controls(self):
        # GPS Data
        self._speed_label = Text(self,
                                 ((5, -5), (260, 195)),
                                 '---',
                                 style={
                                     TEXT_FONT: (PATH_FONT_7SEGM, 150)
                                 }).pack()
        self._speed_unit = Text(self,
                                ((255, 5), (260, 195)),
                                'km/h',
                                style={
                                    TEXT_FONT: (PATH_FONT_VCR, 20)
                                }).pack()
        self._speed_graph = Graph(self,
                                  ((5, 130), (200, 52)),
                                  data_gap_ms=500,
                                  style={
                                      TEXT_COLOR: (150, 150, 150)
                                  }).pack()
        self._speed_graph.prefill_data()

        self._location_label = Text(self,
                                    ((5, 182), (200, 26)),
                                    '---',
                                    style={
                                        TEXT_FONT: (PATH_FONT_VCR, 20)
                                    }).pack()

        # Trip Data
        self._trip_meter = Text(self,
                                ((227, 130), (94, 33)),
                                '----.-',
                                style={
                                    TEXT_FONT: (PATH_FONT_7SEGM, 30)
                                }).pack()

        self._odo_meter = Text(self,
                               ((215, 175), (106, 33)),
                               '------',
                               style={
                                   TEXT_FONT: (PATH_FONT_7SEGM, 30)
                               }).pack()

        self._trip_odo_unit = Text(self,
                                   ((297, 158), (28, 19)),
                                   'km',
                                   style={
                                       TEXT_FONT: (PATH_FONT_VCR, 15)
                                   }).pack()

        # Tab Button
        self._gps_tab_button = Button(self,
                                      ((5, 205), (50, 30)),
                                      'GPS',
                                      style=STYLE_TAB_BUTTON,
                                      command=self._gps_tab_button_command,
                                      state=0).pack()
        self._music_tab_button = Button(self,
                                        ((60, 205), (50, 30)),
                                        'Music',
                                        style=STYLE_TAB_BUTTON,
                                        command=self._clock_tab_button_command).pack()
        self._settings_tab_button = Button(self,
                                           ((115, 205), (50, 30)),
                                           'Settings',
                                           style=STYLE_TAB_BUTTON,
                                           command=self._settings_tab_button_command).pack()

        # Status Bar Icons
        self._ethernet_status_icon = Image(self,
                                           ((175, 205), (32, 32)),
                                           self.get_image(IMG_ETHERNET_OFF)).pack()
        self._wlan0_status_icon = Image(self,
                                        ((205, 205), (32, 32)),
                                        self.get_image(IMG_WIFI_OFF)).pack()
        self._wlan1_status_icon = Image(self,
                                        ((235, 205), (32, 32)),
                                        self.get_image(IMG_WIFI_OFF)).pack()

        # Time Label
        self._time_label = Text(self,
                                ((260, 212), (95, 34)),
                                '--:--',
                                style={
                                    TEXT_FONT: (PATH_FONT_VCR, 20)
                                }).pack()

        # Music Display
        self._current_title = Text(self,
                                   ((5, 5), (310, 30)),
                                   '{Title}',
                                   style={
                                       TEXT_FONT: (PATH_FONT_NORA_MEDIUM, 18)
                                   }).pack()
        self._current_artist = Text(self,
                                    ((5, 40), (310, 30)),
                                    '{Artist}',
                                    style={
                                        TEXT_FONT: (PATH_FONT_NORA_MEDIUM, 15)
                                    }).pack()
        self._current_album = Text(self,
                                   ((5, 60), (310, 30)),
                                   '{Album}',
                                   style={
                                       TEXT_FONT: (PATH_FONT_NORA_MEDIUM, 15)
                                   }).pack()

        # Music Status
        self._current_song_time = Text(self,
                                       ((5, 160), (170, 36)),
                                       '--:--/--:--',
                                       style={
                                           TEXT_FONT: (PATH_FONT_VCR, 20)
                                       }).pack()
        self._current_song_time_bar = ProgressBar(self,
                                                  ((5, 190), (310, 5))).pack()

        # Music Controls
        music_control_style = {
            TEXT_FONT: (PATH_FONT_DEFAULT, 25),
            TEXT_COLOR: (200, 200, 200)
        }
        self._prev_song_button = Button(self,
                                        ((5, 100), (98, 45)),
                                        '<<',
                                        command=self._prev_song_button_command,
                                        style=music_control_style).pack()
        self._play_song_button = Button(self,
                                        ((107, 100), (106, 45)),
                                        '> / ||',
                                        command=self._play_song_button_command,
                                        style=music_control_style).pack()
        self._next_song_button = Button(self,
                                        ((217, 100), (98, 45)),
                                        '>>',
                                        command=self._next_song_button_command,
                                        style=music_control_style).pack()

    def main(self):
        """
        Runs at startup
        """
        self.show_page(CarPiUIApp.PAGE_GPS)
        self._fetcher.start()
        self._predis_fetcher.start()
        # self._settings_tab_button_command(None)

    def update(self):
        """
        Runs every frame
        """
        self._time_label.settext(strftime('%H:%M'))  # Time is the most important thing!

        new_data = self._fetcher.get_current_data()
        new_pers_data = self._predis_fetcher.get_current_data()

        self._set_speed_metrical(new_data)  # We keep the speed updated at all times so the graph does not lag behind
        self._set_networking_data(new_data)  # Networking is kept alive all the time
        self._set_music_player_info(new_data)

        self._set_trip_odo(new_pers_data)

    def shutdown(self):
        try:
            if self.active_window:
                try:
                    self.active_window.destroy()
                finally:
                    pass

            self._fetcher.stop_safe()
            self._predis_fetcher.stop_safe()
            log("Shutting down CarPiUIApp ...")
            self.destroy()
        finally:
            return

    def show_page(self, page_name):
        for name, page in self._pages.iteritems():
            for control in page:  # type: Widget
                if control:
                    control.setvisible(name == page_name)

        self._fetcher.keys_to_fetch = self._redis_pages[page_name]
        self._predis_fetcher.keys_to_fetch = self._predis_pages[page_name]
        self._current_page = page_name

    def _gps_tab_button_command(self, e):
        self._gps_tab_button.setstate(0)
        self._music_tab_button.setstate(1)
        self._settings_tab_button.setstate(1)

        self.show_page(CarPiUIApp.PAGE_GPS)

    def _clock_tab_button_command(self, e):
        self._gps_tab_button.setstate(1)
        self._music_tab_button.setstate(0)
        self._settings_tab_button.setstate(1)

        self.show_page(CarPiUIApp.PAGE_MUSIC)

    def _settings_tab_button_command(self, e):
        # self._gps_tab_button.setstate(1)
        # self._music_tab_button.setstate(1)
        # self._settings_tab_button.setstate(0)
        # self.show_page(CarPiUIApp.PAGE_SETTINGS)
        MainSettingsWindow(self, self._redis, self._pers_redis).show()

    def _prev_song_button_command(self, e):
        send_command_request(self._redis,
                             MpdCommandRedisKeys.COMMAND_PREV)

    def _play_song_button_command(self, e):
        send_command_request(self._redis,
                             MpdCommandRedisKeys.COMMAND_PAUSE)

    def _next_song_button_command(self, e):
        send_command_request(self._redis,
                             MpdCommandRedisKeys.COMMAND_NEXT)

    def _set_speed_metrical(self, data):
        """
        :param dict of str, str data:
        """
        speed_str = ''
        if GpsRedisKeys.KEY_SPEED in data and GpsRedisKeys.KEY_SPEED_KMH in data:
            speed_str = data[GpsRedisKeys.KEY_SPEED_KMH]
        elif ObdRedisKeys.KEY_VEHICLE_SPEED in data:
            speed_str = data[ObdRedisKeys.KEY_VEHICLE_SPEED]
        else:
            speed_str = '-1'

        speed = -1
        try:
            speed = float(speed_str)
        except TypeError:
            speed = -1
        self._set_speed(speed)

        if ObdRedisKeys.KEY_ALIVE in data \
                and (ObdRedisKeys.KEY_ENGINE_RPM in data and data[ObdRedisKeys.KEY_ENGINE_RPM]) \
                and (ObdRedisKeys.KEY_INTAKE_MAP in data and data[ObdRedisKeys.KEY_INTAKE_MAP]) \
                and (ObdRedisKeys.KEY_INTAKE_TEMP in data and data[ObdRedisKeys.KEY_INTAKE_TEMP]):
            try:
                fuel_cons = CarPiUIApp._calc_fuel_consumption(
                    float(data[ObdRedisKeys.KEY_INTAKE_TEMP]),
                    float(data[ObdRedisKeys.KEY_ENGINE_RPM]),
                    float(data[ObdRedisKeys.KEY_INTAKE_MAP]),
                    speed
                )
                if fuel_cons[0] and isnan(fuel_cons[0]):
                    self._set_fuel_consumption(None)
                elif not speed or speed < 20:
                    self._set_fuel_consumption(fuel_cons[0])
                else:
                    self._set_fuel_consumption(fuel_cons[1], True)
            except TypeError:
                self._set_fuel_consumption(None)
        elif GpsRedisKeys.KEY_EPX in data and GpsRedisKeys.KEY_EPY in data\
                and data[GpsRedisKeys.KEY_EPX] and data[GpsRedisKeys.KEY_EPY]:
            self._set_accuracy(
                float(data.get(GpsRedisKeys.KEY_EPX, '0')),
                float(data.get(GpsRedisKeys.KEY_EPY, '0'))
            )
        else:
            self._set_accuracy(None, None)

    def _set_fuel_consumption(self, val, in_lp100k=False):
        if not val or val is str:
            self._location_label.settext('{:>6} l/h'.format('--.--'))
        elif in_lp100k:
            self._location_label.settext('{:>6.2f} l/100km'.format(val))
        else:
            self._location_label.settext('{:>6.2f} l/h'.format(val))

    def _set_accuracy(self, epx, epy):
        if not epx or isnan(epx) or not epy or isnan(epy):
            self._location_label.settext('{0:^15}'.format('NO GPS'))
        else:
            self._location_label.settext('{:>4.0f}m / {:>4.0f}m'.format(epx, epy).center(15))

    def _set_speed(self, speed):
        """
        :param float speed:
        """
        if isnan(speed) or speed < 0:
            self._speed_label.settext('---')
            self._speed_graph.add_data_point(0)
        else:
            self._speed_label.settext('{:>3.0f}'.format(speed))
            self._speed_graph.add_data_point(speed)

    def _set_networking_data(self, data):
        """
        :param dict of str, str data:
        """
        if NetworkInfoRedisKeys.KEY_ETH0_IP in data:
            eth_ip = data[NetworkInfoRedisKeys.KEY_ETH0_IP]
            self._set_ethernet_data(eth_ip is not None and eth_ip != '127.0.0.1' and eth_ip != '::1')
        else:
            self._set_ethernet_data(False)

        if NetworkInfoRedisKeys.KEY_WLAN0_STRENGTH in data \
                and NetworkInfoRedisKeys.KEY_WLAN0_SSID in data:
            strength_str = data[NetworkInfoRedisKeys.KEY_WLAN0_STRENGTH]
            ssid = data[NetworkInfoRedisKeys.KEY_WLAN0_SSID]

            strength = -2
            if ssid is not None:
                strength = int(strength_str) if strength_str else 0

            self._set_wlan_data(self._wlan0_status_icon, strength)
        else:
            self._set_wlan_data(self._wlan0_status_icon, -2)

        if NetworkInfoRedisKeys.KEY_WLAN1_STRENGTH in data \
                and NetworkInfoRedisKeys.KEY_WLAN1_SSID in data:
            strength_str = data[NetworkInfoRedisKeys.KEY_WLAN1_STRENGTH]
            ssid = data[NetworkInfoRedisKeys.KEY_WLAN1_SSID]

            strength = -2
            if ssid is not None:
                strength = int(strength_str) if strength_str else 0

            self._set_wlan_data(self._wlan1_status_icon, strength)
        else:
            self._set_wlan_data(self._wlan1_status_icon, -2)

    def _set_ethernet_data(self, connected):
        """
        :param bool connected:
        """
        self._ethernet_status_icon.setimage(self.get_image(IMG_ETHERNET if connected else IMG_ETHERNET_OFF))

    def _set_wlan_data(self, wlan_status_image, strength):
        """
        :param Image wlan_status_image:
        :param int strength: -2 for disconnected, -1 for unknown
        """
        image = IMG_WIFI_OFF
        if strength < -1:
            pass  # already set for OFF
        elif strength < 25:
            image = IMG_WIFI0
        elif strength < 50:
            image = IMG_WIFI1
        elif strength < 75:
            image = IMG_WIFI2
        else:
            image = IMG_WIFI3
        wlan_status_image.setimage(self.get_image(image))

    def _set_music_player_info(self, data):
        """
        :param dict data:
        """
        if data.get(MpdDataRedisKeys.KEY_ALIVE, None):
            self._set_current_song_tags(unicode(data.get(MpdDataRedisKeys.KEY_SONG_TITLE, ''), 'utf-8'),
                                        unicode(data.get(MpdDataRedisKeys.KEY_SONG_ARTIST, ''), 'utf-8'),
                                        unicode(data.get(MpdDataRedisKeys.KEY_SONG_ALBUM, ''), 'utf-8'))
            self._set_current_song_time(data.get(MpdDataRedisKeys.KEY_CURRENT_TIME, '0:0'),
                                        data.get(MpdDataRedisKeys.KEY_CURRENT_TIME_FORMATTED, '--:--/--:--'))
        else:
            self._set_current_song_tags('[Music Player not running]',
                                        'Check MPD or Daemon',
                                        None)
            self._set_current_song_time('0:0', '--:--/--:--')

        self._set_player_status(data.get(MpdDataRedisKeys.KEY_STATE, None))

    def _set_current_song_tags(self, title, artist, album):
        self._current_title.settext(title if title else '')
        self._current_artist.settext(artist if artist else '')
        self._current_album.settext(album if album else '')

    def _set_current_song_time(self, num_time, format_time):
        self._current_song_time.settext(format_time)

        cur_time, max_time = get_mpd_status_time(num_time)
        self._current_song_time_bar.set_max_value(max_time)
        self._current_song_time_bar.set_value(cur_time)

    def _set_player_status(self, state):
        play_button_icon = ''
        if state and state == 'play':
            play_button_icon = '||'
        else:
            play_button_icon = '>'
        self._play_song_button.settext(play_button_icon)

    def _set_trip_odo(self, data):
        """
        :param dict data:
        """
        trip_a_str = data.get(PersistentGpsRedisKeys.KEY_TRIP_A, -1)
        try:
            self._set_trip(float(trip_a_str))
        except TypeError:
            self._set_trip(float(-1))

        odo_str = data.get(PersistentGpsRedisKeys.KEY_ODO, -1)
        try:
            self._set_odo(float(odo_str))
        except TypeError:
            self._set_odo(float(-1))

    def _set_trip(self, value):
        if isnan(value) or value < 0:
            self._trip_meter.settext('----.-')
        else:
            self._trip_meter.settext('{:>6.1f}'.format(floor(value / 100) / 10))

    def _set_odo(self, value):
        if isnan(value) or value < 0:
            self._odo_meter.settext('------')
        else:
            self._odo_meter.settext('{:>6.0f}'.format(floor(value / 1000)))

    def _network_settings_button_command(self, e):
        CarPiNetworkSettingsWindow(self, self._redis).show()

    def _gps_settings_button_command(self, e):
        pass

    def _music_settings_button_command(self, e):
        pass

    def _power_settings_button_command(self, e):
        CarPiPowerSettingsWindow(self).show()

    @staticmethod
    def _calc_fuel_consumption(intake_temp,
                               rpm,
                               map,
                               speed=None,
                               ve=0.85,
                               vh=1.390,
                               ma=28.9644,
                               r=8.3144598,
                               pf=745):
        """
        Calculates Fuel consumption with the given variables and constants.
        The result is a tuple of ([l/h], [l/100km]).
        Note that if the speed is not given (None) or <1 km/h, fuel efficiency [l/100km]
        will be returned as "None".
        Parameters marked with * are optional
        :param float intake_temp: Intake Air Temperature in [Degrees Celsius]
        :param float rpm: Engine RPM in [RPM]
        :param float map: Intake Manifold Absolute Pressure in [kPa]
        :param float speed: *Speed in [km/h] (or 0 or None to remove fuel efficiency)
        :param float ve: *Volumetric Efficiency (defined as a percentage value, 0 - 1 (100%)), default: 85%
        :param float vh: *Engine Capacity in [l] ([m^3] / 1000), default: 1.39 l
        :param float ma: *avg. molecular mass of air [g/mol], default 28.9644 g/mol
        :param float r: *Gas constant, default 8.3144598 J/(mol.K)
        :param float pf: *Fuel density in [g/l], default 745 g/l (after Super E10, to be adjusted based on fuel type)
        :return tuple of float, float:
        """
        intake_temp_k = intake_temp + 273.15
        imap = rpm * map / intake_temp_k
        maf = (imap / 120) * ve * vh * ma / r

        cons_p_s = (maf / 14.7) / pf
        cons_p_h = cons_p_s * 3600

        if speed and speed >= 1:
            return cons_p_h, cons_p_h / speed * 100
        else:
            return cons_p_h, None


if __name__ == "__main__":
    print("This script is not intended to be run standalone!")
