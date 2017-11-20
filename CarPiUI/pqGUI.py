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
import datetime
import pygame
from pygame.locals import *
from threading import Timer
from math import pi as PI, ceil, isnan

VERSION = (0, 0, 2)
LONG_VERSION = 'v%s.%s.%s' % VERSION
__version__ = LONG_VERSION

# pqStyle Setting Constants
TEXT_FONT_TYPE = 'text font type'
TEXT_FONT = 'text font'
TEXT_ANTI_ALIAS = 'text anti alias'
TEXT_COLOR = 'text color'
TEXT_DISABLED = 'text color disabled'
TEXT_SELECTED = 'text color selected'
TEXT_TITLE = 'text color title'
TEXT_TITLE_INACTIVE = 'text color title inactive'
TEXT_LINE_SPACING = 'text line spacing'

BD_TYPE = 'border type'
BD_DOWN = 'border type down'
BD_HOVER = 'border type hover'
BD_COLOR = 'border color'
BD_SHAD = 'border color shadow'
BD_HIGH = 'border color highlight'
BD_HIGH_SHAD = 'border color highlight shadow'
BD_ACTIVE = 'border color active'

BG_COLOR = 'background color'
BG_BRIGHT = 'background color bright'
BG_LIGHT = 'background color light'
BG_SELECT = 'background color select'
BG_TITLE = 'background color title'
BG_TITLE_GRAD = 'background color gradient'
BG_TITLE_INACTIVE = 'background color title inactive'
BG_TITLE_INACTIVE_GRAD = 'background color title inactive gradient'

TRANS = 'transparent color'

# pqStyle Font types
SYSFONT = 0
FILEFONT = 1

# Border types
BD_NONE = 'border none'
BD_SUNKEN = 'border sunken'
BD_SUNKEN_FLAT = 'border sunken flat'
BD_RAISED = 'border raised'
BD_RAISED_FLAT = 'border raised flat'
BD_SIMPLE_SUNKEN = 'border simple sunken'
BD_SIMPLE_RAISED = 'border simple raised'
BD_FLAT = 'border flat'

import os

# Default pqStyle settings (can be altered in program so generated styles match)
DEFAULT_STYLE = {
    TEXT_FONT_TYPE: FILEFONT,
    #TEXT_FONT: ('Roboto', 11),
    TEXT_FONT: (os.path.join('res', 'fonts', 'Vera.ttf'), 11),
# Note that in DEFAULT_STYLE the TEXT_FONT setting is a sequence yet in a pqStyle instance it is a pygame.font.Font instance (can be passed as a sequence still)
    TEXT_ANTI_ALIAS: True,
    TEXT_COLOR: (255, 255, 255),
    TEXT_DISABLED: (128, 128, 128),
    TEXT_SELECTED: (255, 255, 255),
    TEXT_TITLE: (255, 255, 255),
    TEXT_TITLE_INACTIVE: (212, 208, 200),
    TEXT_LINE_SPACING: 1,

    BD_TYPE: BD_FLAT,
    BD_DOWN: BD_FLAT,
    BD_HOVER: None,  # Can be a border type, or None for no hover effect
    BD_COLOR: (50, 50, 50),
    BD_SHAD: (50, 50, 50),
    BD_HIGH: (50, 50, 50),
    BD_HIGH_SHAD: (50, 50, 50),
    BD_ACTIVE: (0, 0, 0),
# Can be a color for the border around the widget when active, or None to display no border when active

    BG_COLOR: (0, 0, 0),  # (212, 208, 200),
    BG_BRIGHT: (255, 255, 255),
    BG_LIGHT: (233, 231, 227),
    BG_SELECT: (10, 36, 106),
    BG_TITLE: (12, 38, 107),
    BG_TITLE_GRAD: None,
# Can be a color so the active titlebar is a gradient, or None to have a solid titlebar
    BG_TITLE_INACTIVE: (50, 50, 50),
    BG_TITLE_INACTIVE_GRAD: None,
# Can be a color so the inactive titlebar is a gradient, or None to have a solid titlebar

    TRANS: (255, 0, 128),
}
del os

# Event Type Constants
MOUSEDOUBLECLICK = 25
MOUSEENTER = 26
MOUSELEAVE = 27
GAINFOCUS = 28
LOSEFOCUS = 29

# Mouse button constants
M_LEFT = 1
M_SCROLL = 2
M_RIGHT = 3
M_SCROLL_UP = 4
M_SCROLL_DOWN = 5

# Widget State Constants
DISABLED = 0
ENABLED = 1

# Text wrapping constants
WRAP_NONE = 'wrap none'
WRAP_CHAR = 'wrap char'
WRAP_WORD = 'wrap word'

# Window decorator buttons (can be ORed together)
DECO_NONE = 0
DECO_CLOSE = 1
DECO_HELP = 2

# Scrollbar direcions
HORIZONTAL = 'scroll horizontal'
VERTICAL = 'scroll vertical'

# Window decorator buttons icons
DECO_CLOSE_ICON = (
1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0,
0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1)
DECO_HELP_ICON = (
0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0,
0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0)
SCROLL_ARROW_ICON = (
0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1)  # Up
CHECK_MARK = (
0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0,
0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0)


# Rotate: 0 = normal, 1 = 90 CW, 2 = 180, 3 = 90 CCW
def generate_icon(data, size, style, rotate=0, icon=None):
    if isinstance(style, pqStyle):
        style = (style[TEXT_COLOR], style[TRANS])
    if icon is None:
        if rotate & 1:
            icon = pygame.Surface((size[1], size[0]))
        else:
            icon = pygame.Surface(size)
        icon.fill(style[1])
        icon.set_colorkey(style[1])
    icon.lock()
    for n, pixel in enumerate(data):
        if pixel:
            if rotate == 0:
                pos = (n % size[0], n / size[0])
            elif rotate == 1:
                pos = (size[1] - 1 - n / size[0], n % size[0])
            elif rotate == 2:
                pos = (n % size[0], size[1] - 1 - n / size[0])
            else:
                pos = (n / size[0], n % size[0])
            icon.set_at(pos, style[0])
    icon.unlock()
    return icon


def disable_icon(icon, style):
    colors = pygame.surfarray.array3d(icon)
    for y in range(icon.get_height()):
        o = (y + 1) % 2
        for x in range(o, icon.get_width() + o, 2):
            colors[x][y] = style[TRANS]
    disabled = pygame.surfarray.make_surface(colors)
    disabled.set_colorkey(style[TRANS])
    return disabled


def restrict_text(text, style, wsize, wrap=None, color=None, offsets=(4, 4), bg=None):
    if not text:
        return
    text = text.split('\n')
    if wrap is None:
        text = text[0:1]
    if color is None:
        color = style[TEXT_COLOR]
    lines = []
    width, height = 0, 0
    first = True
    for line in text:
        size = style[TEXT_FONT].size(line)
        while line and height + size[1] <= wsize[1] - offsets[1]:
            endtext = ''
            while size[0] and size[0] > wsize[0] - offsets[0]:
                if wrap is None and not first:
                    line = line[:-4] + '...'
                elif wrap == WRAP_CHAR or (wrap is None and first):
                    endtext = line[-1] + endtext
                    line = line[:-1]
                    if wrap is None:
                        first = False
                        line += '...'
                else:
                    temptext = line.split(' ')
                    endtext = temptext[-1] + ' ' + endtext
                    line = ' '.join(temptext[:-1])
                size = style[TEXT_FONT].size(line)
            if size[0] > width:
                width = size[0]
            lines.append(line)
            height += size[1] + style[TEXT_LINE_SPACING]
            if wrap in [WRAP_NONE, None]:
                line = ''
            else:
                line = endtext
                size = style[TEXT_FONT].size(line)
    if lines:
        if wrap is None and not bg:
            return style[TEXT_FONT].render(lines[0], style[TEXT_ANTI_ALIAS], color)
        if len(lines) == 1:
            height -= style[TEXT_LINE_SPACING]
        text_render = pygame.Surface((width, height))
        text_render.fill(style[BG_COLOR])
        y = 0
        for line in lines:
            textrender = style[TEXT_FONT].render(line, style[TEXT_ANTI_ALIAS], color)
            text_render.blit(textrender, (0, y))
            y += textrender.get_height() + style[TEXT_LINE_SPACING]
        return text_render


def rich_restrict_text(text, style, rect, rich_data, wrap=WRAP_WORD, offsets=(4, 4), bg=BG_COLOR):
    if not text:
        return None
    lines = text.split('\n')
    render_data = []
    end_tag = None
    width, height = 0, 0
    linen, charn = 0, 0
    for line in lines:
        render_data.append([[0, 0], [[None, '']]])
        last_space = None
        curline = ''
        objectwidth = 0
        for char in line:
            pos = '%s.%s' % (linen, charn)
            if end_tag is not None and pos == end_tag.end:
                if isinstance(render_data[-1][1][-1], list) and render_data[-1][1][-1][1]:
                    render_data[-1][1].append([None, ''])
                else:
                    render_data[-1][1][-1][0] = None
                end_tag = None
            if pos in rich_data:
                for data in rich_data[pos]:
                    if isinstance(data, RichObject):
                        if render_data[-1][0][0] + data.width > rect.width - offsets[0]:
                            if isinstance(render_data[-1][1][-1], list) and not render_data[-1][1][-1][1]:
                                del render_data[-1][1][-1]
                            if last_space:
                                last_space = None
                            render_data.append([[0, 0], [[None, '']]])
                        if isinstance(render_data[-1][1][-1], list) and render_data[-1][1][-1][1]:
                            render_data[-1][1].append(data)
                        else:
                            render_data[-1][1][-1] = data
                        render_data[-1][1].append([None, ''])
                        objectwidth += data.width
                        if data.height > render_data[-1][0][1]:
                            render_data[-1][0][1] = data.height
                    elif isinstance(data, RichTag) and end_tag is None:
                        end_tag = data
                        if isinstance(render_data[-1][1][-1], list) and render_data[-1][1][-1][1]:
                            render_data[-1][1].append([data, ''])
                        else:
                            render_data[-1][1][-1][0] = data
            size = style[TEXT_FONT].size(curline + char)
            if size[0] + objectwidth > rect.width - offsets[0]:
                if isinstance(render_data[-1][1][-1], tuple) and not render_data[-1][1][-1][1]:
                    del render_data[-1][1][-1]
                if char == ' ' or wrap != WRAP_WORD or not last_space:
                    if render_data[-1][0][0] > width:
                        width = render_data[-1][0][0]
                    height += render_data[-1][0][1] + style[TEXT_LINE_SPACING]
                    render_data.append([[0, 0], [[None, '']]])
                    curline = ''
                    objectwidth = 0
                else:
                    render_data[-1][0] = last_space[2:4]
                    if render_data[-1][0][0] > width:
                        width = render_data[-1][0][0]
                    height += render_data[-1][0][1] + style[TEXT_LINE_SPACING]
                    render_data.append([[size[0] - last_space[2], max(size[1], last_space[4])],
                                        [[render_data[-1][1][last_space[0]][0], '']]])
                    if len(render_data[-2][1][last_space[0]][1]) >= last_space[1]:
                        curline = render_data[-2][1][last_space[0]][1][last_space[1]:]
                        render_data[-1][1][-1][1] = curline
                        render_data[-2][1][last_space[0]][1] = render_data[-2][1][last_space[0]][1][:last_space[1]]
                    while last_space[0] + 1 < len(render_data[-2][1]):
                        curline += render_data[-2][1][last_space[0] + 1][1]
                        render_data[-1][1].append(render_data[-2][1][last_space[0] + 1])
                        del render_data[-2][1][last_space[0] + 1]
                    last_space = None
            else:
                render_data[-1][0][0] = size[0] + objectwidth
                if char == ' ':
                    last_space = [len(render_data[-1][1]) - 1, len(render_data[-1][1][-1][1]) + 1,
                                  render_data[-1][0][0], render_data[-1][0][1], 0]
                elif last_space and size[1] > last_space[4]:
                    last_space[4] = size[1]
            curline += char
            if size[1] > render_data[-1][0][1]:
                render_data[-1][0][1] = size[1]
            render_data[-1][1][-1][1] += char
            charn += 1
        if render_data[-1][0][0] > width:
            width = render_data[-1][0][0]
        height += render_data[-1][0][1] + style[TEXT_LINE_SPACING]
        linen += 1
        charn = 0
    if len(render_data) == 1:
        height -= style[TEXT_LINE_SPACING]
    render = pygame.Surface((width, height))
    render.fill(style[bg])
    curstyle = None
    y = 0
    for line in render_data:
        x = 0
        for sect in line[1]:
            if isinstance(sect, list):
                if sect[0] is None:
                    curstyle = style
                else:
                    curstyle = sect[0].style
                text = curstyle[TEXT_FONT].render(sect[1], curstyle[TEXT_ANTI_ALIAS], curstyle[TEXT_COLOR],
                                                  curstyle[BG_COLOR])
                width, height = text.get_size()
                cury = y + line[0][1] / 2 - height / 2
                render.blit(text, (x, cury))
                if sect[0] is not None:
                    sect[0].topleft = (x, cury)
                    sect[0].size = (width, height)
                    sect[0].real_position = True
                x += width
            else:
                cury = y + line[0][1] / 2 - sect.height / 2
                sect.topleft = (x, cury)
                sect.real_position = True
                sect.draw(render)
                x += sect.width
        y += line[0][1] + style[TEXT_LINE_SPACING]
    return render


def draw_border(screen, rect, style, type, active=False, bg=True):
    if not isinstance(rect, pygame.Rect):
        rect = pygame.Rect(rect)
    all = ((rect.x - 2, rect.y - 2), (rect.width + 4, rect.height + 4))
    allsmall = ((rect.x - 1, rect.y - 1), (rect.width + 2, rect.height + 2))
    if bg:
        pygame.draw.rect(screen, style[BG_COLOR], rect)
    if type == BD_NONE:
        if active and style[BD_ACTIVE]:
            pygame.draw.rect(screen, style[BD_ACTIVE], allsmall, 1)
    elif type in [BD_FLAT, BD_SIMPLE_SUNKEN, BD_SIMPLE_RAISED]:
        if active and style[BD_ACTIVE]:
            pygame.draw.rect(screen, style[BD_ACTIVE], all, 1)
        if type == BD_FLAT:
            pygame.draw.rect(screen, style[BD_COLOR], allsmall, 1)
        else:
            if type == BD_SIMPLE_RAISED:
                high, shad = style[BD_HIGH], style[BD_SHAD]
            else:
                high, shad = style[BD_SHAD], style[BD_HIGH]
            pygame.draw.lines(screen, shad, False,
                              [(rect.x - 1, rect.y + rect.height), (rect.x + rect.width, rect.y + rect.height),
                               (rect.x + rect.width, rect.y - 1)])
            pygame.draw.lines(screen, high, False, [(rect.x - 1, rect.y + rect.height - 1), (rect.x - 1, rect.y - 1),
                                                    (rect.x + rect.width - 1, rect.y - 1)])
    elif type in [BD_SUNKEN, BD_RAISED, BD_SUNKEN_FLAT, BD_RAISED_FLAT]:
        if active and style[BD_ACTIVE]:
            pygame.draw.rect(screen, style[BD_ACTIVE], ((rect.x - 3, rect.y - 3), (rect.width + 6, rect.height + 6)), 1)
        if type in [BD_RAISED, BD_RAISED_FLAT]:
            high, darkhigh, shad, darkshad = style[BD_HIGH], style[BD_HIGH_SHAD], style[BD_SHAD], style[BD_COLOR]
        else:
            high, darkhigh, shad, darkshad = style[BD_SHAD], style[BD_COLOR], style[BD_HIGH_SHAD], style[BD_HIGH]
        if type in [BD_SUNKEN_FLAT, BD_RAISED_FLAT]:
            if bg:
                pygame.draw.rect(screen, style[BG_COLOR], allsmall)
            pygame.draw.rect(screen, high, all, 1)
        else:
            pygame.draw.lines(screen, high, False, [(rect.x - 2, rect.y + rect.height), (rect.x - 2, rect.y - 2),
                                                    (rect.x + rect.width, rect.y - 2)])
            pygame.draw.lines(screen, darkhigh, False,
                              [(rect.x - 1, rect.y + rect.height - 1), (rect.x - 1, rect.y - 1),
                               (rect.x + rect.width - 1, rect.y - 1)])
            pygame.draw.lines(screen, shad, False,
                              [(rect.x - 1, rect.y + rect.height), (rect.x + rect.width, rect.y + rect.height),
                               (rect.x + rect.width, rect.y - 1)])
            pygame.draw.lines(screen, darkshad, False, [(rect.x - 2, rect.y + rect.height + 1),
                                                        (rect.x + rect.width + 1, rect.y + rect.height + 1),
                                                        (rect.x + rect.width + 1, rect.y - 2)])


class pqEvent:
    def __init__(self, event):
        if isinstance(event, dict):
            self.key = event.get('key', None)
            self.button = event.get('button', None)
            self.pos = event.get('pos', None)
            self.rel = event.get('rel', None)
            self.type = event.get('type', 0)
        else:
            self.key = None
            self.button = None
            self.pos = None
            self.rel = None
            self.type = event.type
            if hasattr(event, 'key'):
                self.key = event.key
            if hasattr(event, 'pos'):
                self.pos = event.pos
            if hasattr(event, 'button'):
                self.button = event.button
            if hasattr(event, 'rel'):
                self.rel = event.rel
        self.done = True

    def __str__(self):
        if self.type in [MOUSEDOUBLECLICK, MOUSEENTER, MOUSELEAVE, GAINFOCUS, LOSEFOCUS]:
            name = ['MouseDoubleClick', 'MouseEnter', 'MouseLeave', 'GainFocus', 'LoseFocus'][self.type - USEREVENT - 1]
        else:
            name = pygame.event.event_name(self.type)
        return '<pqEvent:%s(%s) [K:%s][B:%s][P:%s][R:%s]>' % (
        name, self.type, self.key, self.button, self.pos, self.rel)


class pqStyle:
    def __init__(self, style=None):
        if isinstance(style, pqStyle):
            self.style = dict(style.style)
        else:
            self.style = dict(DEFAULT_STYLE)
            if isinstance(style, dict):
                self.style.update(style)
            if not isinstance(self.style[TEXT_FONT], pygame.font.Font):
                if self.style[TEXT_FONT_TYPE] == SYSFONT:
                    self.style[TEXT_FONT] = pygame.font.SysFont(*self.style[TEXT_FONT])
                else:
                    self.style[TEXT_FONT] = pygame.font.Font(*self.style[TEXT_FONT])

    def copy(self, update=None):
        copy = pqStyle(self)
        if update:
            copy.style.update(update)
        return copy

    def get(self, index, default=None):
        return self.style.get(index, default)

    def __getitem__(self, index):
        return self.style[index]

    def __setitem__(self, index, value):
        self.style[index] = value

    def __contains__(self, item):
        return item in self.style


class RichTag(pygame.Rect):
    def __init__(self, name, start, end, style):
        self.name = name
        self.style = style
        self.start = start
        self.end = end
        self.real_position = False
        pygame.Rect.__init__(self, ((0, 0), (0, 0)))

    def __str__(self):
        return '<RichTag[%s][%s,%s][%s,%s,%s,%s]>' % (
        self.name, self.start, self.end, self.x, self.y, self.width, self.height)


class RichObject(pygame.Rect):
    def __init__(self, name, position, size, object):
        self.name = name
        self.position = position
        self.object = object
        self.real_position = False
        pygame.Rect.__init__(self, ((0, 0), size))

    def draw(self, screen):
        if self.real_position and isinstance(self.object, pygame.Surface):
            screen.blit(self.object, self.topleft)

    def __str__(self):
        return '<RichObject[%s][%s][%s,%s,%s,%s]>' % (self.name, self.position, self.x, self.y, self.width, self.height)


class StringVariable:
    def __init__(self, value, maxlength=None, excludechrs=[], callback=None):
        self.value = ''
        self.maxlength = None
        self.excludechrs = []
        self.callback = callback
        self.set(value)

    def get(self):
        return self.value

    def set(self, value, check=True):
        value = str(value)
        if check:
            if self.maxlength:
                value = value[:self.maxlength]
            for c in value:
                if c in self.excludechrs:
                    return
        self.value = value
        if self.callback:
            self.callback(value)

    def __str__(self):
        return self.value


class IntegerVariable:
    def __init__(self, value, range=[None, None], callback=None):
        self.value = '0'
        self.range = range
        self.callback = callback
        self.set(value)

    def get(self):
        return int(self.value)

    def set(self, value, check=True):
        value = str(value)
        if check:
            try:
                val = int(value)
                if (self.range[0] is not None and val < self.range[0]) or (self.range[1] is not None and val > self.range[1]):
                    return
            except:
                return
        self.value = value
        if self.callback:
            self.callback(int(value))


class FloatVariable:
    def __init__(self, value, range=[None, None], precision=None, callback=None):
        self.value = '0'
        self.range = range
        self.callback = callback
        self.set(value)

    def get(self):
        return float(self.value)

    def set(self, value, check=True):
        value = str(value)
        if check:
            try:
                val = float(value)
                if (self.range[0] is not None and val < self.range[0]) or (self.range[1] is not None and val > self.range[1]):
                    return
            except:
                return
        if precision and '.' in value:
            value = value[:value.index('.') + precision + 1]
        self.value = value
        if self.callback:
            self.callback(float(value))


class Widget(pygame.Rect):
    default_style = {BD_TYPE: BD_NONE}
    border_offsets = (0, 0, 0, 0)  # left, top, right, bottom
    edge_offsets = (0, 0)  # left, top
    steal_focus = False
    widget_name = 'Widget'
    special_shape = False

    def __init__(self, parent, rect=((0, 0), (0, 0)), style=None, state=ENABLED):
        self.parent = parent
        if isinstance(parent, pqApp):
            self.app = parent
        else:
            self.app = parent.app
        if isinstance(parent, Window) or isinstance(parent, Popup):
            self.window = parent
        elif parent is None:
            self.window = self.app
        else:
            self.window = parent.window
        if style is None:
            self.style = pqStyle(self.default_style)
        else:
            defaultstyle = dict(self.default_style)
            if isinstance(style, dict):
                defaultstyle.update(style)
                self.style = pqStyle(defaultstyle)
            else:
                defaultstyle.update(style.style)
                self.style = defaultstyle
        self.binds = {}
        self.state = state
        self.visible = True
        pygame.Rect.__init__(self, rect)

    def pack(self):
        self.parent.pack_widget(self)
        return self

    def draw(self, screen, position, bg=True):
        if not self.visible:
            return
        if isinstance(self.window, Window):
            active = self.window.active == self
        else:
            active = False
        if self in self.app.mouseover and self.style[BD_HOVER]:
            type = self.style[BD_HOVER]
        elif self.app.pressed == self:
            type = self.style[BD_DOWN]
        else:
            type = self.style[BD_TYPE]
        draw_border(screen, self.move(position), self.style, type, active, bg)

    def bind(self, event, callback, add=False):
        if isinstance(event, tuple):
            type, key = event
        else:
            type, key = event, None
        if type in [KEYDOWN, KEYUP, MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN]:
            if not type in self.binds:
                self.binds[type] = {}
            if add:
                if not key in self.binds:
                    self.binds[type][key] = []
                if not callback in self.binds[type][key]:
                    self.binds[type][key].append(callback)
            else:
                self.binds[type][key] = [callback]
        elif type in [MOUSEENTER, MOUSELEAVE, MOUSEDOUBLECLICK]:
            if not type in self.binds:
                self.binds[type] = []
            if not add:
                self.binds[type] = [callback]
            elif not callback in self.binds[type]:
                self.binds[type].append(callback)

    def setstate(self, state):
        self.state = state

    def setvisible(self, visible):
        self.visible = visible

    def execbind(self, event):
        if not self.visible:
            return
        if isinstance(event, dict):
            event = pqEvent(event)
        if event.type in self.binds:
            callbacks = []
            if event.type in [KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
                if event.type in [KEYDOWN, KEYUP] and event.key in self.binds[event.type]:
                    callbacks = self.binds[event.type][event.key]
                elif event.type in [MOUSEBUTTONDOWN, MOUSEBUTTONUP] and event.button in self.binds[event.type]:
                    callbacks = self.binds[event.type][event.button]
            else:
                callbacks = self.binds[event.type]
            for callback in callbacks:
                callback(event)

    def process_event(self, event, mouseover=[]):
        if not self.visible:
            return
        if event.type in [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEDOUBLECLICK]:
            if event.type == MOUSEBUTTONDOWN and self.steal_focus:
                self.window.active = self
            elif event.type == MOUSEBUTTONUP and self.app.pressed:
                self.app.pressed = None
            if not self in self.app.mouseover:
                self.execbind({'type': MOUSEENTER, 'pos': event.pos})
            if not self in mouseover:
                mouseover.append(self)
        self.execbind(event)

    def __eq__(self, other):
        return id(self) == id(other)

    def destroy(self):
        self.app.destroy(self)

    def after(self, time, callback):
        return self.app.after(time, callback)

    def after_cancel(self, id):
        self.app.after_cancel(id)

    def special_contain(self, position):
        return True

    def __repr__(self):
        return '<%s(%s,%s,%s,%s)>' % (self.widget_name, self.x, self.y, self.width, self.height)

    def __str__(self):
        return self.__repr__()


class Canvas(Widget):
    default_style = {BD_TYPE: BD_NONE}
    widget_name = 'Canvas'

    # bg is only the starting background color, it doesn't have any effect after initialization. None for BG_COLOR
    def __init__(self, parent, rect, style=None, bg=None, state=ENABLED):
        Widget.__init__(self, parent, rect, style, state)
        self.surface = pygame.Surface(self.size)
        if bg is None:
            self.surface.fill(self.style[BG_COLOR])
        else:
            self.surface.fill(bg)

    def draw(self, screen, position):
        if not self.visible:
            return
        Widget.draw(self, screen, position)
        screen.blit(self.surface, (self.x + position[0], self.y + position[1]))


class Button(Widget):
    default_style = {BD_TYPE: BD_RAISED, BD_DOWN: BD_SUNKEN_FLAT}
    steal_focus = True
    widget_name = 'Button'

    def __init__(self, parent, rect, text, command=None, style=None, icon=None, state=ENABLED):
        self.command = command
        self.text = None
        self.text_render = [None, None]
        self.icon = [icon, None]
        Widget.__init__(self, parent, rect, style, state)
        self.settext(text)
        self.bind((MOUSEBUTTONUP, M_LEFT), self.callback)

    def settext(self, text):
        self.text = text
        restrict = 4
        if self.icon[0]:
            restrict += self.icon[0].get_width() + 2
        self.text_render = [restrict_text(text, self.style, self.size, offsets=(restrict, 4)), None]

    def seticon(self, icon):
        self.icon = [icon, None]
        if self.text:
            self.settext(self.text)

    def draw(self, screen, position):
        if not self.visible:
            return
        Widget.draw(self, screen, position)
        down = 0
        if self.app.pressed == self:
            down = 1
        width = 0
        text = None
        if self.text:
            if self.state == DISABLED:
                if not self.text_render[1]:
                    self.text_render[1] = restrict_text(self.text, self.style, self.size,
                                                        color=self.style[TEXT_DISABLED])
                text = self.text_render[1]
            else:
                text = self.text_render[0]
            if text:
                width = text.get_width()
        icon = None
        if self.icon[0] and self.icon[0].get_height() <= self.height - 4:
            if self.state == DISABLED:
                if not self.icon[1]:
                    self.icon[1] = disable_icon(self.icon[0], self.style)
                icon = self.icon[1]
            else:
                icon = self.icon[0]
            if width:
                width += 4
            width += icon.get_width()
        mid = (self.x + position[0] + self.width / 2, self.y + position[1] + self.height / 2)
        if text:
            screen.blit(text, (mid[0] + width / 2 - text.get_width() + down, mid[1] - text.get_height() / 2 + down))
        if icon:
            screen.blit(icon, (mid[0] - width / 2 + down, mid[1] - icon.get_height() / 2 + down))

    def callback(self, event):
        if self.command and self.state == ENABLED and self.visible:
            self.command(event)

    def process_event(self, event, mouseover=[]):
        if not self.visible:
            return
        if event.type in [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN]:
            if event.type == MOUSEBUTTONDOWN and event.button == M_LEFT:
                if self.steal_focus:
                    self.window.active = self
                if self.state == ENABLED:
                    self.app.pressed = self
            elif event.type == MOUSEBUTTONUP and event.button == M_LEFT:
                if self.app.pressed == self:
                    self.execbind(event)
                self.app.pressed = None
                return
            if not self in mouseover:
                mouseover.append(self)
        self.execbind(event)


class Radio(Widget):
    default_style = {BD_TYPE: BD_NONE, BD_DOWN: BD_NONE}
    steal_focus = False
    widget_name = 'Radio'

    def __init__(self, parent, rect, text, value, variable, style=None, state=ENABLED):
        self.text = None
        self.text_render = [None, None]
        self.value = value
        self.variable = variable
        Widget.__init__(self, parent, rect, style, state)
        self.settext(text)
        self.bind((MOUSEBUTTONUP, M_LEFT), self.callback)

    def settext(self, text):
        self.text = text
        self.text_render = [restrict_text(text, self.style, self.size, offsets=(18, 4)), None]

    def draw(self, screen, position):
        if not self.visible:
            return
        Widget.draw(self, screen, position)
        position = [position[0] + self.x, position[1] + self.y + self.height / 2]
        if self.state == DISABLED:
            if not self.text_render[1]:
                self.text_render[1] = restrict_text(self.text, self.style, self.size, color=self.style[TEXT_DISABLED],
                                                    offsets=(18, 4))
            text = self.text_render[1]
        else:
            text = self.text_render[0]
        if text:
            screen.blit(text, (position[0] + 16, position[1] - text.get_height() / 2))
        position[0] += 8
        a = (PI / 4.0)
        pygame.draw.circle(screen, self.style[[BG_BRIGHT, BG_COLOR][self.app.pressed == self]],
                           (position[0], position[1]), 5)
        pygame.draw.arc(screen, self.style[BD_SHAD], ((position[0] - 6, position[1] - 6), (12, 12)), a, 5 * a)
        pygame.draw.arc(screen, self.style[BD_COLOR], ((position[0] - 5, position[1] - 5), (10, 10)), a, 5 * a)
        pygame.draw.arc(screen, self.style[BD_HIGH], ((position[0] - 6, position[1] - 6), (12, 12)), 5 * a, 9 * a)
        pygame.draw.arc(screen, self.style[BG_COLOR], ((position[0] - 5, position[1] - 5), (10, 10)), 5 * a, 9 * a)
        if self.variable.get() == self.value:
            pygame.draw.circle(screen, self.style[[TEXT_COLOR, TEXT_DISABLED][self.state == DISABLED]],
                               (position[0], position[1]), 2)

    def callback(self, event):
        if self.state == ENABLED and self.visible:
            self.variable.set(self.value)

    def process_event(self, event, mouseover=[]):
        if not self.visible:
            return
        if event.type in [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN]:
            if event.type == MOUSEBUTTONDOWN and event.button == M_LEFT:
                if self.steal_focus:
                    self.window.active = self
                if self.state == ENABLED:
                    self.app.pressed = self
            elif event.type == MOUSEBUTTONUP and event.button == M_LEFT:
                if self.app.pressed == self:
                    self.execbind(event)
                self.app.pressed = None
                return
            if not self in mouseover:
                mouseover.append(self)
        self.execbind(event)


class Check(Radio):
    # default_style = {BD_TYPE:BD_NONE,BD_DOWN:BD_NONE}
    # steal_focus = False
    widget_name = 'Check'

    def __init__(self, parent, rect, text, onvalue, offvalue, variable, style=None, state=ENABLED):
        self.offvalue = offvalue
        self.check = None
        Radio.__init__(self, parent, rect, text, onvalue, variable, style, state)

    # def settext(self, text):
    # self.text = text
    # self.text_render = [restrict_text(text, self.style, self.size, offsets=(18,4)),None]

    def draw(self, screen, position):
        if not self.visible:
            return
        Widget.draw(self, screen, position)
        position = [position[0] + self.x, position[1] + self.y + self.height / 2]
        if self.state == DISABLED:
            if not self.text_render[1]:
                self.text_render[1] = restrict_text(self.text, self.style, self.size, color=self.style[TEXT_DISABLED],
                                                    offsets=(18, 4))
            text = self.text_render[1]
        else:
            text = self.text_render[0]
        if text:
            screen.blit(text, (position[0] + 16, position[1] - text.get_height() / 2))
        draw_border(screen, ((position[0] + 2, position[1] - 5), (10, 10)),
                    self.style.copy({BG_COLOR: self.style[[BG_BRIGHT, BG_COLOR][self.app.pressed == self]]}), BD_SUNKEN)
        if self.variable.get() == self.value:
            if not self.check:
                self.check = generate_icon(CHECK_MARK, (8, 8), self.style)
            screen.blit(self.check, (position[0] + 3, position[1] - 4))

    def callback(self, event):
        if self.state == ENABLED and self.visible:
            if self.variable.get() == self.value:
                self.variable.set(self.offvalue)
            else:
                self.variable.set(self.value)

            # def process_event(self, event, mouseover=[]):
            # if event.type in [MOUSEMOTION,MOUSEBUTTONUP,MOUSEBUTTONDOWN]:
            # if event.type == MOUSEBUTTONDOWN and event.button == M_LEFT:
            # if self.steal_focus:
            # self.window.active = self
            # if self.state == ENABLED:
            # self.app.pressed = self
            # elif event.type == MOUSEBUTTONUP and event.button == M_LEFT:
            # if self.app.pressed == self:
            # self.execbind(event)
            # self.app.pressed = None
            # return
            # if not self in mouseover:
            # mouseover.append(self)
            # self.execbind(event)


class Box(Widget):
    widget_name = 'Box'

    def __init__(self, parent, rect, text=None, style=None, state=ENABLED):
        self.text = ''
        self.text_render = None
        Widget.__init__(self, parent, rect, style, state)
        self.settext(text)

    def settext(self, text):
        self.text = text
        self.text_render = restrict_text(text, self.style, self.size, bg=True)

    def draw(self, screen, position):
        if not self.visible:
            return
        realrect = self.move(position)
        offset = 0
        if self.text_render:
            offset = self.text_render.get_height() / 2
        pygame.draw.rect(screen, self.style[BD_HIGH], (
        (realrect.x - 1, realrect.y - 1 - offset), (realrect.width + 2, realrect.height + 2 + offset)), 1)
        pygame.draw.rect(screen, self.style[BD_SHAD], (
        (realrect.x - 2, realrect.y - 2 - offset), (realrect.width + 2, realrect.height + 2 + offset)), 1)
        if self.text_render:
            screen.blit(self.text_render, (realrect.x + 5, realrect.y - self.text_render.get_height()))

    def setstate(self, state):
        Widget.setstate(self, state)
        self.settext(self.text)


class Image(Widget):
    def __init__(self, parent, rect, image, style=None, state=ENABLED):
        Widget.__init__(self, parent, rect, style, state)
        self.image = image  # type: pygame.Surface

    def setimage(self, image):
        self.image = image

    def draw(self, screen, position, bg=True):
        Widget.draw(self, screen, position)
        if isinstance(self.image, pygame.Surface) \
                and self.image.get_size() <= (self.width, self.height) \
                and self.state:
            screen.blit(self.image, (self.x + position[0] + 10 - self.image.get_width() / 2,
                                     self.y + position[1] + self.height / 2 - self.image.get_height() / 2))


class ProgressBar(Widget):
    def __init__(self, parent, rect, max_val=0, min_val=0, style=None, state=ENABLED):
        Widget.__init__(self, parent, rect, style, state)
        self._value = 0
        self._min_value = min_val
        self._max_value = max_val

    def set_value(self, val):
        self._value = val

    def set_max_value(self, val):
        self._max_value = val

    def set_min_value(self, val):
        self._min_value = val

    def draw(self, screen, position, bg=True):
        """
        :param pygame.SurfaceType screen:
        :param position:
        :param bg:
        :return:
        """
        if not self.visible:
            return

        Widget.draw(self, screen, position)

        # Calculate Progress Bar Percentage
        percentage = 0
        val_span = self._max_value - self._min_value
        if val_span <= 0:
            percentage = 0
        else:
            zero_based_value = self._value - self._min_value
            percentage = min((zero_based_value * (100 / val_span)) / 100, 1)

        fill_rect = Rect(self.x + position[0],
                         self.y + position[1],
                         self.width * percentage,
                         self.height)
        pygame.draw.rect(screen, self.style[TEXT_COLOR], fill_rect, 0)

        # Border
        pygame.draw.rect(screen,
                         self.style[BD_COLOR],
                         Rect(self.x + position[0], self.y + position[1], self.width, self.height),
                         1)


class Graph(Widget):
    def __init__(self, parent, rect, data=[], data_gap_ms=500, style=None, state=ENABLED):
        Widget.__init__(self, parent, rect, style, state)
        self._data = data
        self._last_added = None
        self._data_gap_ms = data_gap_ms

    def add_data_point(self, val):
        if self._last_added \
                and (datetime.datetime.now() - self._last_added).microseconds < self._data_gap_ms * 1000:
            return

        if isnan(val):
            val = 0

        self._data.append(val)
        self._data = self._data[-self.get_max_data_points():]
        self._last_added = datetime.datetime.now()

    def get_max_data_points(self):
        return self.width - 2

    def prefill_data(self):
        for i in range(0, self.get_max_data_points()):
            self._data.append(0)

    @staticmethod
    def round_up_to_10(v):
        return int(ceil(v / 10.0)) * 10

    def draw(self, screen, position, bg=True):
        if not self.visible:
            return

        Widget.draw(self, screen, position)

        # Draw Data
        min_item = float(0)
        max_item = float(self.round_up_to_10(max(max(self._data), 10)))
        height = float(self.height - 2)
        max_p = self.get_max_data_points()

        # Values
        for i, data_point in enumerate(self._data):
            rel_val = (height / max_item) * data_point
            pygame.draw.line(screen,
                             self.style[TEXT_COLOR],
                             (self.x + i + 1, ceil(self.y + height + 1)),
                             (self.x + i + 1, ceil(self.y + height + 1 - rel_val)))

        # Scale
        for i in range(0, int(max_item), 10):
            if i % 20 == 10 and max_item > 50:
                continue

            rel_val = (height / max_item) * float(i)
            pygame.draw.line(screen,
                             self.style[BD_COLOR],
                             (self.x, ceil(self.y + height + 1 - rel_val)),
                             (self.x + self.width - 1, ceil(self.y + height + 1 - rel_val)))

        # Border
        pygame.draw.rect(screen,
                         self.style[BD_COLOR],
                         Rect(self.x + position[0], self.y + position[1], self.width, self.height),
                         1)


class Text(Widget):
    default_style = {BD_TYPE: BD_NONE}
    widget_name = 'Text'

    # wrap: none, char, word
    def __init__(self, parent, rect, text, style=None, wrap=WRAP_CHAR, state=ENABLED):
        self.wrap = wrap
        Widget.__init__(self, parent, rect, style, state)
        self.settext(text)

    def settext(self, text):
        self.text = text
        self.text_render = restrict_text(text, self.style, self.size, self.wrap)

    def draw(self, screen, position):
        if not self.visible:
            return
        Widget.draw(self, screen, position)
        if self.text_render:
            screen.blit(self.text_render, (self.x + position[0], self.y + position[1]))


class RichText(Widget):
    default_style = {BD_TYPE: BD_NONE}
    widget_name = 'RichText'

    # wrap: none, char, word
    def __init__(self, parent, rect, text, style=None, wrap=WRAP_WORD, state=ENABLED):
        self.wrap = wrap
        self.rich_data = {}
        self.text = None
        self.text_render = None
        Widget.__init__(self, parent, rect, style, state)
        self.view = pygame.Rect((0, 0), (self.width - 2, self.height - 2))
        self.viewsize = list(self.size)
        if text:
            self.settext(text)

    def tag_add(self, name, start, end, style):
        if not start in self.rich_data:
            self.rich_data[start] = []
        self.rich_data[start].append(RichTag(name, start, end, style))

    def object_add(self, name, position, size, object):
        if not position in self.rich_data:
            self.rich_data[position] = []
        self.rich_data[position].append(RichObject(name, position, size, object))

    def settext(self, text):
        self.text = text
        if self.rich_data:
            self.text_render = rich_restrict_text(text, self.style, self, self.rich_data, self.wrap, bg=BG_COLOR)
        else:
            self.text_render = restrict_text(text, self.style, self.size, self.wrap)
        self.viewsize = (
        max(self.text_render.get_width(), self.view.width), max(self.text_render.get_height(), self.view.height))

    def draw(self, screen, position):
        if not self.visible:
            return
        Widget.draw(self, screen, position)
        if self.text_render:
            container = pygame.Surface(self.size)
            container.fill(self.style[BG_COLOR])
            container.blit(self.text_render, (2, 2), self.view)
            screen.blit(container, (self.x + position[0], self.y + position[1]))


class Container(Widget):
    default_style = {BD_TYPE: BD_SUNKEN}
    widget_name = 'Container'

    def __init__(self, parent, rect, style=None, xscroll=None, yscroll=None, state=ENABLED):
        self.widgets = []
        self.xscroll = xscroll
        if xscroll is not None:
            self.xscroll.viewwidget = self
        self.yscroll = yscroll
        if yscroll is not None:
            self.yscroll.viewwidget = self
        Widget.__init__(self, parent, rect, style, state)
        self.view = pygame.Rect((0, 0), self.size)
        self.viewsize = list(self.size)

    def setview(view):
        self.view.topleft = (self.x + view[0], self.y + view[1])

    def draw(self, screen, position):
        if not self.visible:
            return
        realrect = self.move(position)
        Widget.draw(self, screen, position)
        container = pygame.Surface(self.size)
        container.fill(self.style[BG_COLOR])
        for index in self.view.collidelistall(self.widgets):
            self.widgets[index].draw(container, (-self.view.x, -self.view.y))
        screen.blit(container, realrect.topleft)

    def pack_widget(self, widget):
        if not isinstance(widget, Window) and not isinstance(widget, Popup):
            self.widgets.append(widget)
            maxx, maxy = widget.x + widget.width + 4, widget.y + widget.height + 4
            if maxx > self.viewsize[0]:
                self.viewsize[0] = maxx
                if self.xscroll is not None:
                    self.xscroll.setbar((self.view.x / float(maxx), self.view.right / float(maxx)), False)
            if maxy > self.viewsize[1]:
                self.viewsize[1] = maxy
                if self.yscroll is not None:
                    self.yscroll.setbar((self.view.y / float(maxy), self.view.bottom / float(maxy)), False)

    def process_event(self, event, mouseover=[]):
        if not self.visible:
            return
        if event.type in [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEDOUBLECLICK]:
            if not self in self.app.mouseover:
                self.execbind({'type': MOUSEENTER, 'pos': (event.pos[0] - self.x, event.pos[1] - self.y)})
            if not self in mouseover:
                mouseover.append(self)
            indexs = pygame.Rect(event.pos, (1, 1)).collidelistall(self.widgets)
            if indexs:
                for index in indexs:
                    widget = self.widgets[index]
                    if widget.special_shape and not widget.special_contains(event.pos):
                        continue
                    if not widget in self.app.mouseover:
                        widget.execbind({'type': MOUSEENTER, 'pos': (event.pos[0] - widget.x, event.pos[1] - widget.y)})
                    if not widget in mouseover:
                        mouseover.append(widget)
                event.pos = (event.pos[0] - widget.x, event.pos[1] - widget.y)
                widget.process_event(event, mouseover)
                return
        if event.type == MOUSEBUTTONUP and self.app.pressed:
            self.app.pressed = None
        self.execbind(event)

    def xview(self, position):
        self.view.x = (self.viewsize[0] - self.width) * position

    def yview(self, position):
        self.view.y = (self.viewsize[1] - self.height) * position


class ScrollbarBar(Widget):
    default_style = {BD_TYPE: BD_RAISED}
    widget_name = 'ScrollbarBar'

    def __init__(self, parent, direction, style):
        self.direction = direction
        Widget.__init__(self, parent, ((2, 2), (12, 12)), style)

    def process_event(self, event, mouseover=[]):
        if not self.visible:
            return
        if event.type == MOUSEBUTTONDOWN and event.button == M_LEFT:
            self.app.drag = self
            self.app.dragoffset = event.pos
        else:
            self.execbind(event)

    def drag(self, event, offset):
        if self.direction == HORIZONTAL:
            self.x = min(max(event.pos[0] - offset[0], 18), self.parent.width - self.width - 18)
            bar = (self.x - 18) / float(self.parent.width - 40)
        else:
            self.y = min(max(event.pos[1] - offset[1], 18), self.parent.height - self.height - 18)
            bar = (self.y - 18) / float(self.parent.height - 40)
        self.parent.setbar((bar, bar + self.parent.bar[1] - self.parent.bar[0]))


class Scrollbar(Container):
    default_style = {BD_TYPE: BD_NONE}
    button_times = [400, 50]
    widget_name = 'Scrollbar'

    def __init__(self, parent, rect, style=None, direction=HORIZONTAL, view=None, state=ENABLED):
        self.timer = None
        self.direction = direction
        self.viewwidget = view
        Container.__init__(self, parent, rect, style, state=DISABLED)
        i = generate_icon(SCROLL_ARROW_ICON, (8, 4), self.style, [0, 3][direction == HORIZONTAL])
        self.decrease = Button(self, ((2, 2), (12, 12)), '', icon=i, state=DISABLED)
        self.decrease.steal_focus = False
        self.decrease.bind((MOUSEBUTTONDOWN, M_LEFT), lambda e: self.buttondown(-1, e))
        self.decrease.bind((MOUSEBUTTONUP, M_LEFT), self.buttonup)
        self.decrease.pack()
        if direction == HORIZONTAL:
            self.height = 16
            if self.width < 32:
                self.width = 32
            self.increase = Button(self, ((self.width - 14, 2), (12, 12)), '',
                                   icon=generate_icon(SCROLL_ARROW_ICON, (8, 4), self.style, 1), state=DISABLED)
        else:
            self.width = 16
            if self.height < 32:
                self.height = 32
            self.increase = Button(self, ((2, self.height - 14), (12, 12)), '',
                                   icon=generate_icon(SCROLL_ARROW_ICON, (8, 4), self.style, 2), state=DISABLED)
        self.increase.steal_focus = False
        self.increase.bind((MOUSEBUTTONDOWN, M_LEFT), lambda e: self.buttondown(1, e))
        self.increase.bind((MOUSEBUTTONUP, M_LEFT), self.buttonup)
        self.increase.pack()
        self.scrollbar = ScrollbarBar(self, direction, style)
        self.setbar((0, 1))
        if state == ENABLED:
            self.scrollbar.pack()

    def buttondown(self, direction, event=None):
        size = self.bar[1] - self.bar[0]
        if (direction == 1 and self.bar[0] < 1 - size) or (direction == -1 and self.bar[0] > 0):
            bar = self.bar[0] + 0.01 * direction
            self.setbar((bar, bar + size))
            if self.timer is not None and event is None:
                time = self.button_times[1]
            else:
                time = self.button_times[0]
            self.timer = self.after(time, lambda d=direction: self.buttondown(d))

    def buttonup(self, event):
        if self.timer is not None:
            self.after_cancel(self.timer)
            self.timer = None

    def setbar(self, bar, view=True):
        self.bar = [max(min(bar[0], 1), 0), max(min(bar[1], 1), 0)]
        if self.bar == [0, 1]:
            self.state = DISABLED
            self.decrease.state = DISABLED
            self.increase.state = DISABLED
        else:
            self.state = ENABLED
            self.decrease.state = ENABLED
            self.increase.state = ENABLED
        if self.direction == HORIZONTAL:
            self.scrollbar.x = 18 + (self.width - 40) * bar[0]
            if bar[1] == 1:
                self.scrollbar.width = self.width - 18 - self.scrollbar.x
            else:
                self.scrollbar.width = 21 + (self.width - 40) * bar[1] - self.scrollbar.x
            if view and self.viewwidget is not None:
                self.viewwidget.xview(self.bar[0] / (1 - (self.bar[1] - self.bar[0])))
        else:
            self.scrollbar.y = 18 + (self.height - 40) * bar[0]
            if bar[1] == 1:
                self.scrollbar.height = self.height - 18 - self.scrollbar.y
            else:
                self.scrollbar.height = 21 + (self.height - 40) * bar[1] - self.scrollbar.y
            if view and self.viewwidget is not None:
                self.viewwidget.yview(self.bar[0] / (1 - (self.bar[1] - self.bar[0])))

    def draw(self, screen, position):
        if not self.visible:
            return
        realrect = self.move(position)
        Widget.draw(self, screen, position)
        container = pygame.Surface(self.size)
        container.fill(self.style[BG_LIGHT])
        for index in self.view.collidelistall(self.widgets):
            self.widgets[index].draw(container, (-self.view.x, -self.view.y))
        screen.blit(container, realrect.topleft)


class PopupItem(Widget):
    steal_focus = False
    widget_name = 'PopupItem'

    def __init__(self, parent, text, callback, style=None, icon=None, state=ENABLED):
        self.text_render = None
        self.callback = callback
        self.text_render = [None, None, None]
        self.icon = [None, None]
        if isinstance(icon, pygame.Surface) and icon.get_size() <= (16, 16):
            self.icon[0] = icon
        Widget.__init__(self, parent, ((0, parent.height), (parent.width, 20)), style, state)
        self.settext(text)
        self.bind((MOUSEBUTTONUP, M_LEFT), self.execute)

    def execute(self, event):
        if self.state == ENABLED:
            self.parent.destroy(True)
            if self.callback:
                self.callback(event)

    def settext(self, text=None):
        self.text = text
        self.text_render = [restrict_text(text, self.style, self.size), None, None]
        height = 1
        if self.text_render:
            height = self.text_render[0].get_height()
        self.height = max(20, height)

    def draw(self, screen, position):
        selected = (self.parent.selected == -1 and self in self.app.mouseover) or (
        self.parent.selected > -1 and self.parent.widgets[self.parent.selected] == self)
        pygame.draw.rect(screen, self.style[[BG_COLOR, BG_SELECT][selected]], self)
        icon = None
        text = None
        if self.state == ENABLED:
            icon = self.icon[0]
            if selected:
                if not self.text_render[2]:
                    self.text_render[2] = restrict_text(self.text, self.style, self.size,
                                                        color=self.style[TEXT_SELECTED])
                text = self.text_render[2]
            else:
                text = self.text_render[0]
        else:
            if self.icon[1]:
                icon = self.icon[1]
            elif self.icon[0]:
                icon = self.icon[1] = disable_icon(self.icon[0], self.style)
            if not self.text_render[1]:
                self.text_render[1] = restrict_text(self.text, self.style, self.size, color=self.style[TEXT_DISABLED])
            text = self.text_render[1]
        if icon:
            screen.blit(icon, (self.x + position[0] + 10 - icon.get_width() / 2,
                               self.y + position[1] + self.height / 2 - icon.get_height() / 2))
        if text:
            screen.blit(text,
                        (self.x + position[0] + 20, self.y + position[1] + self.height / 2 - text.get_height() / 2))


class SubPopupItem(PopupItem):
    popup_delay = 200
    widget_name = 'SubPopupItem'

    def __init__(self, parent, text, popup, style=None, icon=None, state=ENABLED):
        self.popup = popup
        self.timer = -1
        PopupItem.__init__(self, parent, text, style, icon, state)
        self.arrow = [
            generate_icon(SCROLL_ARROW_ICON, (8, 4), self.style, 1),
            generate_icon(SCROLL_ARROW_ICON, (8, 4), (self.style[BD_HIGH], self.style[TRANS]), 1),
            None,
            None
        ]

    def execute(self, event=None):
        pass

    def draw(self, screen, position):
        PopupItem.draw(self, screen, position)
        selected = (self.parent.selected == -1 and self in self.app.mouseover) or (
        self.parent.selected > -1 and self.parent.widgets[self.parent.selected] == self)
        if self.state == ENABLED:
            arrow = self.arrow[selected]
        else:
            if self.arrow[2 + selected]:
                arrow = self.arrow[2 + selected]
            else:
                arrow = self.arrow[2 + selected] = disable_icon(self.arrow[0 + selected], self.style)
        screen.blit(arrow, (self.x + position[0] + self.width - 10 - arrow.get_width() / 2,
                            self.y + position[1] + self.height / 2 - arrow.get_height() / 2))

    def do_popup(self):
        self.popup.show((self.parent.x + self.topright[0] - 2, self.parent.y + self.y))

    def process_event(self, event, mouseover=[]):
        if event.type == MOUSEENTER and self.app.active_popup == self.parent:
            self.timer = self.after(self.popup_delay, self.do_popup)
        elif event.type == MOUSELEAVE and self.timer > -1:
            self.after_cancel(self.timer)
            self.timer = -1
        PopupItem.process_event(self, event, mouseover)


class PopupSeperator(Widget):
    steal_focus = False
    widget_name = 'PopupSeperator'

    def __init__(self, parent, style):
        Widget.__init__(self, parent, ((0, parent.height), (parent.width, 10)), style=style)

    def draw(self, screen, position):
        pygame.draw.rect(screen, self.style[BG_COLOR], self)
        pygame.draw.line(screen, self.style[BD_SHAD], (self.x, self.y + 4), (self.x + self.width, self.y + 4))
        pygame.draw.line(screen, self.style[BD_HIGH], (self.x, self.y + 5), (self.x + self.width, self.y + 5))


class Popup(Container):
    default_style = {BD_TYPE: BD_RAISED}
    edge_offsets = (0, 0)
    steal_focus = False
    widget_name = 'Popup'

    def __init__(self, parent, style=None):
        self.selected = -1
        Container.__init__(self, parent, ((0, 0), (100, 0)), style, state=ENABLED)

    def add_widget(self, widget):
        self.widgets.append(widget)
        self.height += widget.height
        self.view.height += widget.height

    def addseperator(self):
        self.add_widget(PopupSeperator(self, self.style))

    def additem(self, text, callback, style=None, icon=None, state=ENABLED):
        self.add_widget(PopupItem(self, text, callback, style, icon, state))

    def addsubpopup(self, text, popup, style=None, icon=None, state=ENABLED):
        self.add_widget(SubPopupItem(self, text, popup, style, icon, state))

    def draw(self, screen, position):
        Widget.draw(self, screen, position)
        container = pygame.Surface(self.size)
        container.fill(self.style[BG_COLOR])
        for index in self.view.collidelistall(self.widgets):
            self.widgets[index].draw(container, position)
        screen.blit(container, (position[0] + self.x, position[1] + self.y))

    def show(self, position):
        self.topleft = (position[0] + 2, position[1] + 2)
        self.app.show_widget(self)

    def process_event(self, event, mouseover=[]):
        if event.type == KEYDOWN:
            if event.key in [K_UP, K_DOWN]:
                if event.key == K_UP:
                    offset = len(self.widgets) - 1
                else:
                    offset = 1
                index = (self.selected + offset) % len(self.widgets)
                while isinstance(self.widgets[index], PopupSeperator) and index != self.selected:
                    index = (index + offset) % len(self.widgets)
                self.selected = index
        elif event.type in [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEDOUBLECLICK]:
            if not self in self.app.mouseover:
                self.execbind({'type': MOUSEENTER, 'pos': (event.pos[0] - self.x, event.pos[1] - self.y)})
            if not self in mouseover:
                mouseover.append(self)
            index = pygame.Rect(event.pos, (1, 1)).collidelist(self.widgets)
            if index != -1:
                if index != self.selected and self.app.active_popup != self:
                    self.app.active_popup.destroy(self)
                widget = self.widgets[index]
                if widget.special_shape and not widget.special_contains(event.pos):
                    return
                if not widget in self.app.mouseover:
                    widget.execbind({'type': MOUSEENTER, 'pos': (event.pos[0] - widget.x, event.pos[1] - widget.y)})
                if not widget in mouseover:
                    mouseover.append(widget)
                self.selected = index
                event.pos = (event.pos[0] - widget.x, event.pos[1] - widget.y)
                widget.process_event(event, mouseover)
                return
            elif self.app.active_popup == self:
                self.selected = -1
        elif event.type == MOUSELEAVE and self.app.active_popup == self:
            self.selected = -1
        if event.type == MOUSEBUTTONUP and self.app.pressed:
            self.app.pressed = None
        self.execbind(event)

    def destroy(self, parent=None):
        self.selected = -1
        if (parent == True and isinstance(self.parent, Popup)) or (isinstance(parent, Popup) and parent != self.parent):
            self.parent.destroy(parent)
        Container.destroy(self)


class Window(Container):
    default_style = {BD_TYPE: BD_RAISED}
    edge_offsets = (0, 21)
    steal_focus = True
    restrict_position = False
    widget_name = 'Window'

    def __init__(self, parent, rect, title, style=None, icon=None, buttons=DECO_NONE, modal=False):
        self.icon = None
        if isinstance(icon, pygame.Surface) and icon.get_size() <= (16, 16):
            self.icon = icon
        self.active = None
        self.buttons = buttons
        self.modal = modal
        Container.__init__(self, parent, rect, style, state=ENABLED)
        self.title_bar = [None, None]
        self.title_render = [None, None]
        if title is not None:
            self.top -= 21
            self.height += 21
        else:
            self.title = None
        self.settitle(title)
        self.closedeco = None
        self.helpdeco = None
        if buttons:
            position = self.width - 16
            for deco in (DECO_CLOSE, DECO_HELP):
                if buttons & deco:
                    if deco == DECO_CLOSE:
                        self.closedeco = Button(self, ((position, -17), (12, 12)), '', self.close, {BD_DOWN: BD_SUNKEN},
                                                generate_icon(DECO_CLOSE_ICON, (8, 7), self.style))
                        self.closedeco.steal_focus = False
                        self.closedeco.pack()
                    elif deco == DECO_HELP:
                        self.helpdeco = Button(self, ((position, -17), (12, 12)), '', self.help, {BD_DOWN: BD_SUNKEN},
                                               generate_icon(DECO_HELP_ICON, (8, 8), self.style))
                        self.helpdeco.steal_focus = False
                        self.helpdeco.pack()
                    position -= 18

    def settitle(self, title):
        self.title = title
        restrict = 4
        if self.icon:
            restrict += 18
        if self.buttons:
            for deco in [DECO_CLOSE, DECO_HELP]:
                if self.buttons & deco:
                    restrict += 18
        self.title_render = [
            restrict_text(title, self.style, self.size, color=self.style[TEXT_TITLE], offsets=(restrict, 4)), None]

    def draw(self, screen, position):
        self.update()
        Widget.draw(self, screen, position)
        container = pygame.Surface(self.size)
        container.fill(self.style[BG_COLOR])
        if self.title is not None:
            offset = 0
            if self.icon:
                offset = 18
            if self.app.active_window == self:
                bg = self.style[BG_TITLE]
                bggrad = self.style[BG_TITLE_GRAD]
                title = self.title_render[0]
                titlebar = self.title_bar[0]
            else:
                bg = self.style[BG_TITLE_INACTIVE]
                bggrad = self.style[BG_TITLE_INACTIVE_GRAD]
                if not self.title_render[1]:
                    restrict = 4
                    if self.icon:
                        restrict += 18
                    if self.buttons:
                        for deco in [DECO_CLOSE, DECO_HELP]:
                            if self.buttons & deco:
                                restrict += 18
                    self.title_render[1] = restrict_text(self.title, self.style, self.size,
                                                         color=self.style[TEXT_TITLE_INACTIVE], offsets=(restrict, 4))
                title = self.title_render[1]
                titlebar = self.title_bar[1]
            if not titlebar:
                titlebar = pygame.Surface((self.width, 20))
                if self.style[BG_TITLE_GRAD]:
                    width = self.width / 40.0
                    coloroffset = tuple((bg[c] - bggrad[c]) / 40.0 for c in range(3))
                    for x in range(40):
                        pygame.draw.rect(titlebar, tuple(bg[c] - coloroffset[c] * x for c in range(3)),
                                         ((width * x, 0), (width, 20)))
                else:
                    titlebar.fill(bg)
                self.title_bar[self.app.active_window != self] = titlebar
            container.blit(titlebar, position)
            if title:
                container.blit(title,
                               (position[0] + 2 + offset, position[1] + 10 - self.title_render[0].get_height() / 2))
            if self.icon:
                container.blit(self.icon, (10 - self.icon.get_width() / 2, 10 - self.icon.get_height() / 2))
        if self.buttons:
            for index, deco in enumerate((DECO_CLOSE, DECO_HELP)):
                if self.buttons & deco:
                    self.widgets[index].draw(container, (position[0], position[1] + 21))
        for index in self.view.collidelistall(self.widgets):
            self.widgets[index].draw(container, (position[0], position[1] + 21))
        screen.blit(container, (position[0] + self.x, position[1] + self.y))

    def help(self, event=None):
        pass

    def close(self, event=None):
        self.destroy()

    def update(self):
        pass

    def process_event(self, event, mouseover=[]):
        if event.type in [KEYDOWN, KEYUP]:
            if self.active:
                self.active.process_event(event)
            else:
                self.execbind(event)
                return
            if not event.done:
                self.execbind(event)
        elif event.type in [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEDOUBLECLICK]:
            if not self in self.app.mouseover:
                self.execbind({'type': MOUSEENTER, 'pos': (event.pos[0] - self.x, event.pos[1] - self.y)})
            if not self in mouseover:
                mouseover.append(self)
            indexs = pygame.Rect(event.pos, (1, 1)).collidelistall(self.widgets)
            if indexs:
                for index in indexs:
                    widget = self.widgets[index]
                    if not widget in self.app.mouseover:
                        widget.execbind({'type': MOUSEENTER, 'pos': (event.pos[0] - widget.x, event.pos[1] - widget.y)})
                    if not widget in mouseover:
                        mouseover.append(widget)
                event.pos = (event.pos[0] - widget.x, event.pos[1] - widget.y)
                widget.process_event(event, mouseover)
                return
        if event.type == MOUSEBUTTONUP and self.app.pressed:
            self.app.pressed = None
        elif event.type == MOUSEBUTTONDOWN and event.button == M_LEFT and event.pos[1] < 0:
            self.app.drag = self
            self.app.dragoffset = event.pos
            return
        self.execbind(event)

    def drag(self, event, offset):
        pos = (event.pos[0] - offset[0], event.pos[1] - self.edge_offsets[1] - offset[1])
        if self.restrict_position:
            pos = (max(min(pos[0], self.app.width - self.width), 0), max(min(pos[1], self.app.height - self.height), 0))
        self.topleft = pos

    def show(self, active=True):
        self.app.show_widget(self, active)


class pqApp(Window):
    double_click_speed = 400  # Max number of milliseconds between clicks to register double click
    widget_name = 'pqApp'

    def __init__(self, rect, title, style=None, fullscreen=False):
        self.windows = []
        self.active_window = None
        self.popups = []
        self.active_popup = None
        self.mouseover = []
        self.running = True
        self.pressed = None
        self.drag = None
        self.dragoffset = None
        self.queue = []
        self.timers = {}
        self.timerid = 0
        self.fullscreen = None
        self.doubleclick = None
        Window.__init__(self, self, ((0, 0), rect), title, style)
        self.setfullscreen(fullscreen)
        self.bind(QUIT, self.exit)

    def settitle(self, title):
        self.title = title
        pygame.display.set_caption(title)

    # None to toggle
    def setfullscreen(self, fullscreen=None):
        if fullscreen is None:
            fullscreen = not self.fullscreen
        if fullscreen != self.fullscreen:
            if fullscreen:
                self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
                self.bind((KEYDOWN, K_ESCAPE), self.exit, True)
            else:
                self.screen = pygame.display.set_mode(self.size)
                if KEYDOWN in self.binds and K_ESCAPE in self.binds[KEYDOWN] and self.exit in self.binds[KEYDOWN][
                    K_ESCAPE]:
                    self.binds[KEYDOWN][K_ESCAPE].remove(self.exit)

    def enddoubleclick(self):
        if self.doubleclick:
            self.doubleclick.cancel()
            self.doubleclick = None

    def run(self):
        self.clock = pygame.time.Clock()
        self.main()
        while self.running:
            for pygameevent in pygame.event.get():
                event = pqEvent(pygameevent)
                if self.drag:
                    if event.type == MOUSEMOTION:
                        widget = self.drag.parent
                        while widget != self:
                            event.pos = (event.pos[0] - widget.x, event.pos[1] - widget.y)
                            widget = widget.parent
                        self.drag.drag(event, self.dragoffset)
                    else:
                        self.drag = None
                        self.dragoffset = None
                elif self.popups and event.type in [KEYDOWN, KEYUP]:
                    self.active_popup.process_event(event)
                else:
                    mouseover = []
                    if event.type == MOUSEBUTTONDOWN:
                        if event.button == M_LEFT:
                            if self.doubleclick:
                                self.process_event(pqEvent({'type': MOUSEDOUBLECLICK, 'pos': event.pos}))
                                self.doubleclick.cancel()
                                self.doubleclick = None
                            else:
                                self.doubleclick = Timer(self.double_click_speed / 1000.0, self.enddoubleclick)
                                self.doubleclick.start()
                        elif self.doubleclick:
                            self.doubleclick.cancel()
                            self.doubleclick = None
                    self.process_event(event, mouseover)
                    if event.type in [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEDOUBLECLICK]:
                        for widget in self.mouseover:
                            if not widget in mouseover:
                                widget.process_event(pqEvent(
                                    {'type': MOUSELEAVE, 'pos': (event.pos[0] - widget.x, event.pos[1] - widget.y)}))
                        for widget in mouseover:
                            if not widget in self.mouseover:
                                widget.process_event(pqEvent(
                                    {'type': MOUSEENTER, 'pos': (event.pos[0] - widget.x, event.pos[1] - widget.y)}))
                        self.mouseover = mouseover
            self.update()
            self.draw(self.screen, (0, 0))
            if self.queue:
                for callback in self.queue:
                    callback()
                self.queue = []
            self.clock.tick(30)
        self.close()

    def draw(self, screen, position):
        self.screen.fill(self.style[BG_COLOR])
        for index in self.view.collidelistall(self.widgets):
            self.widgets[index].draw(self.screen, (0, 0))
        for window in self.windows + self.popups:
            window.draw(self.screen, (0, 0))
        # self.screen.blit(self.style[TEXT_FONT].render(str(self.clock.get_fps()), self.style[TEXT_ANTI_ALIAS],
        # self.style[TEXT_COLOR]), (0,0))
        pygame.display.flip()

    def bind(self, event, callback, add=False):
        if isinstance(event, tuple):
            type, key = event
        else:
            type, key = event, None
        if type in [KEYDOWN, KEYUP, MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN]:
            if not type in self.binds:
                self.binds[type] = {}
            if add:
                if not key in self.binds[type]:
                    self.binds[type][key] = []
                if not callback in self.binds[type][key]:
                    self.binds[type][key].append(callback)
            else:
                self.binds[type][key] = [callback]
        else:
            if add:
                if not type in self.binds:
                    self.binds[type] = []
                if not callback in self.binds[type]:
                    self.binds[type].append(callback)
            else:
                self.binds[type] = [callback]

    def main(self):
        self.exit()

    def show_widget(self, window, active=True):
        if isinstance(window, Window):
            self.windows.append(window)
            if active:
                self.app.set_active(window)
        elif isinstance(window, Popup):
            self.app.popups.append(window)
            self.app.active_popup = window

    def raiseup(self, window):
        self.windows.append(window)
        del self.windows[self.windows.index(window)]

    def set_active(self, widget):
        if isinstance(widget, Window) or isinstance(widget, Popup):
            self.active_window = widget
            self.raiseup(widget)
        else:
            widget.window.active = widget

    def process_event(self, event, mouseover=[]):
        if event.type in [KEYDOWN, KEYUP] and self.active_window:
            self.active_window.process_event(event)
            return
        elif event.type in [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEDOUBLECLICK]:
            indexs = pygame.Rect(event.pos, (1, 1)).collidelistall(self.windows + self.popups)
            if indexs:
                for index in indexs:
                    if index >= len(self.windows):
                        window = self.popups[index - len(self.windows)]
                    else:
                        window = self.windows[index]
                    if window.special_shape and not window.special_contain(event.pos):
                        continue
                    if not window in self.app.mouseover and (not self.app.modal or self.app.active_window == window):
                        window.execbind({'type': MOUSEENTER, 'pos': (
                        event.pos[0] - window.x, event.pos[1] - window.y - window.edge_offsets[1])})
                    if not window in mouseover:
                        mouseover.append(window)
                process = True
                if self.app.active_window and self.app.active_window != window and self.app.active_window.modal:
                    parent = window.parent
                    while parent != self:
                        parent = parent.parent
                        if parent == window:
                            break
                    else:
                        process = False
                if process:
                    if isinstance(window,
                                  Window) and event.type == MOUSEBUTTONDOWN and self.app.active_window != window:
                        self.set_active(window)
                    event.pos = (event.pos[0] - window.x, event.pos[1] - window.y - window.edge_offsets[1])
                    window.process_event(event, mouseover)
                if event.type == MOUSEBUTTONDOWN and self.popups and not isinstance(window, Popup):
                    for popup in self.popups:
                        popup.destroy()
                return
            elif event.type == MOUSEBUTTONDOWN:
                if self.app.active_window and not self.app.modal:
                    self.app.active_window = None
                if self.popups:
                    for popup in self.popups:
                        popup.destroy()
        Window.process_event(self, event, mouseover)

    def after(self, time, callback):
        self.timers[self.timerid] = Timer(time / 1000.0, lambda c=callback, id=self.timerid: self.after_run(c, id))
        self.timers[self.timerid].start()
        self.timerid += 1
        return self.timerid - 1

    def after_cancel(self, id):
        if id in self.timers:
            self.timers[id].cancel()
            del self.timers[id]

    def after_run(self, callback, id):
        if id in self.timers:
            del self.timers[id]
            self.queue.append(callback)

    def exit(self, event=None):
        self.running = False

    def destroy(self, widget=None):
        if widget is None:
            self.exit()
        else:
            self.queue.append(lambda w=widget: self.destroy_widget(w))

    def destroy_widget(self, widget):
        if isinstance(widget, Window):
            if self.active_window == widget:
                if isinstance(widget.parent, Window):
                    self.active_window = widget.parent
                    if GAINFOCUS in self.active_window.binds:
                        execbind(self.active_window, {'type': GAINFOCUS})
                else:
                    if GAINFOCUS in self.binds:
                        execbind(self, {'type': GAINFOCUS})
                    self.active_window = None
            self.windows.remove(widget)
            pygame.event.post(pygame.event.Event(MOUSEMOTION, pos=pygame.mouse.get_pos(), rel=(0, 0)))
        elif isinstance(widget, Popup):
            if self.active_popup == widget:
                self.active_popup = widget.parent
            self.popups.remove(widget)
        else:
            if widget.parent.active == widget:
                widget.parent.active = None
            widget.parent.widgets.remove(widget)
