#!/usr/bin/env bash
# MIT License
#
# Copyright (c) 2017 Raphael "rGunti" Guntersweiler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This script is based on the following StackOverflow article and their sources:
#  - https://raspberrypi.stackexchange.com/a/11898

### Settings ##########################
TIMEZONE=Europe/Berlin
GPS_TIME_VARIATION=0
### ###################################

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

echo Preparing ...

# Date Time Reset
date -s '01/01/2010 00:00' > /dev/null
sleep 1

# Kill Services
pkill ntpd
pkill gpsd

# Start Monitoring GPS
echo Starting GPS ...
gpsd -b -n -D 2 /dev/ttyUSB0
sleep 2

# Get GPS Date
echo Getting GPS Time ...
GPSDATE=`gpspipe -w | head -10 | grep TPV | sed -r 's/.*"time":"([^"]*)".*/\1/' | head -1`

# Set Date
echo "Setting Time (Timezone: $TIMEZONE, Variation: $GPS_TIME_VARIATION seconds) ..."
TZ='$TIMEZONE' date -s "$GPSDATE $GPS_TIME_VARIATION seconds" > /dev/null

# Start NTPD
echo Starting NTPD ...
ntpd

echo " ======== Script has ended ======== "
