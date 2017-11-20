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

from pqGUI import Window, DECO_CLOSE, Scrollbar, VERTICAL, BG_COLOR, Container, Widget, BG_LIGHT


class CarPiSettingsWindow(Window):
    def __init__(self, parent, icon=None):
        Window.__init__(self,
                        parent,
                        ((0, 19), (320, 220)),
                        'Settings',
                        icon=icon,
                        style={ BG_COLOR: (100, 100, 100) },
                        buttons=DECO_CLOSE,
                        modal=True)

        self._scrollbar = Scrollbar(self,
                                    ((304, 0), (16, 220)),
                                    style={BG_LIGHT: (25, 25, 25)},
                                    direction=VERTICAL).pack()
        self._container = Container(self,
                                    ((0, 0), (304, 220)),
                                    yscroll=self._scrollbar).pack()
        Widget(self._container,
               ((50, 50), (260, 260)),
               {BG_COLOR: (150, 150, 150)}).pack()


if __name__ == "__main__":
    print("This script is not intended to be run standalone!")
