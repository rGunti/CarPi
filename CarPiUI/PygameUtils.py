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

import pygame
from os import environ
from CarPiLogging import log
from ConfigParser import ConfigParser

IO_CONFIG_SECTION = 'IO'
IO_CONFIG_KEY_OUTPUT_DEVICE = 'output'
IO_CONFIG_KEY_MOUSE_DRIVER = 'mouse_driver'
IO_CONFIG_KEY_MOUSE_DEVICE = 'mouse_device'

ENV_OUTPUT = 'SDL_FBDEV'
ENV_MOUSE_DRIVER = 'SDL_MOUSEDRV'
ENV_MOUSE_DEVICE = 'SDL_MOUSEDEV'

UI_CONFIG_SECTION = 'UI'
UI_CONFIG_KEY_SHOW_MOUSE = 'show_mouse'
UI_CONFIG_KEY_FULLSCREEN = 'fullscreen'
UI_CONFIG_KEY_RES_WIDTH = 'res_width'
UI_CONFIG_KEY_RES_HEIGHT = 'res_height'


def init_pygame(config):
    """
    :param ConfigParser config:
    :return:
    """
    log('Initializing PyGame ...')
    pygame.init()

    mouse_visible = False
    if config.has_option(UI_CONFIG_SECTION, UI_CONFIG_KEY_SHOW_MOUSE):
        mouse_visible = config.getboolean(UI_CONFIG_SECTION,
                                          UI_CONFIG_KEY_SHOW_MOUSE)

    pygame.mouse.set_visible(mouse_visible)
    pygame.display.set_mode((config.getint(UI_CONFIG_SECTION, UI_CONFIG_KEY_RES_WIDTH),
                             config.getint(UI_CONFIG_SECTION, UI_CONFIG_KEY_RES_HEIGHT)))


def init_io(config):
    """
    :param ConfigParser config:
    :return:
    """
    log("Configuring PyGame IO ...")

    if ENV_OUTPUT not in environ:
        if config.has_option(IO_CONFIG_SECTION, IO_CONFIG_KEY_OUTPUT_DEVICE):
            environ[ENV_OUTPUT] = config.get(IO_CONFIG_SECTION,
                                             IO_CONFIG_KEY_OUTPUT_DEVICE)

    if ENV_MOUSE_DEVICE not in environ:
        if config.has_option(IO_CONFIG_SECTION, IO_CONFIG_KEY_MOUSE_DEVICE):
            environ[ENV_MOUSE_DEVICE] = config.get(IO_CONFIG_SECTION,
                                                   IO_CONFIG_KEY_MOUSE_DEVICE)

    if ENV_MOUSE_DRIVER not in environ:
        if config.has_option(IO_CONFIG_SECTION, IO_CONFIG_KEY_MOUSE_DRIVER):
            environ[ENV_MOUSE_DRIVER] = config.get(IO_CONFIG_SECTION,
                                                   IO_CONFIG_KEY_MOUSE_DRIVER)


def load_image(path, convert_alpha=True):
    image = None
    try:
        log('Loading Image {} ...'.format(path))
        with open(path) as f:
            image = pygame.image.load(f)  # type: pygame.Surface

        if image and convert_alpha:
            image = image.convert_alpha(image)
    except IOError:
        log('Could not load image {}!'.format(path))
    except pygame.error as err:
        log('PyGame did a bad while loading "{}": {}'.format(path, err.message))

    return image


if __name__ == "__main__":
    print("This script is not intended to be run standalone!")
