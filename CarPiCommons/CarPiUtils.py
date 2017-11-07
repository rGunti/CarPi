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


def format_time(sec, no_hours=False):
    """
    Formats a time given in seconds into (hh:)mm:ss
    :param float sec: Seconds
    :param bool no_hours: If True, the formatter will not add hours and instead
    display all minutes (e.g. "61 minutes" instead of "1 hour and 1 minute")
    :return str:
    """
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    if h >= 1:
        if no_hours:
            return "%02d:%02d" % ((h * 60) + m, s)
        else:
            return "%d:%02d:%02d" % (h, m, s)
    else:
        return "%02d:%02d" % (m, s)


def format_mpd_status_time(v, both=False):
    """
    Formats a MPD-given time
    :param str v: Value given from MPD (usually a string value with
    2 integer values separated by a Colon ":", both values representing seconds)
    :param bool both: If True, both values will be formatted, else only the left
    (first) value
    :return str:
    """
    arr_v = v.split(':')

    time_current = format_time(int(arr_v[0]), True)
    if both:
        time_total = format_time(int(arr_v[1]), True)
        return time_current + '/' + time_total
    else:
        return time_current


if __name__ == "__main__":
    print("This script is not intended to be run standalone!")
