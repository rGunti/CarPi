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


def init_pygame():
    log('Initializing PyGame ...')
    pygame.init()

    pygame.mouse.set_visible(environ.get('SHOW_MOUSE', '0') == '1')
    pygame.display.set_mode((320, 240))


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
