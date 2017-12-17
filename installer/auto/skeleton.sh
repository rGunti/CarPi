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

# Print Status Info in Updater Progress Bar
# $1 => Message
# $2 => Percentage (0 - 100)
function setStatus {
	echo XXX
	echo $2
	echo $1
	echo XXX
}

# Copy a file from $2 to $1
function copyFile {
    DESTINATION=$1
    SOURCE=$2
    cp -f "$2" "$1"
}

# Copy array of files $1 to $2 with a given Status text $3
function copyFileArray {
    declare -a files=("${!1}")
    fileCount=${#files[@]}
    c=0

    for (( i=0; i<${fileCount}; i++ ));
    do
        setStatus "$3\n$(basename ${i})" $(awk "BEGIN {printf \"%.0f\n\", $i / $fileCount * 100}")
        copyFile "$2" "${i}"
    done
}

# Helper Vars
SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INSTALL_SOURCE="$SCRIPT_LOCATION/../../"
INSTALL_DESTINATION="/usr/bin/carpi/"
CONFIG_DESTINATION="/etc/carpi/"

DIR_COMMONS="$INSTALL_SOURCE/CarPiCommons"
DIR_DAEMONS="$INSTALL_SOURCE/CarPiDaemons"

RES_FILES=(
    "$DIR_COMMONS/CarPiConfig.py"
    "$DIR_COMMONS/CarPiLogging.py"
    "$DIR_COMMONS/CarPiThreading.py"
    "$DIR_COMMONS/CarPiUtils.py"
    "$DIR_COMMONS/RedisKeys.py"
    "$DIR_COMMONS/RedisUtils.py"
)
DAEMON_FILES=(
    "$DIR_DAEMONS/GpsDaemon.py"
    "$DIR_DAEMONS/Obd2Daemon.py"
    "$DIR_DAEMONS/Obd2DataParser.py"
    "$DIR_DAEMONS/MpdDataAndControlDaemon.py"
    "$DIR_DAEMONS/NetworkInfoDaemon.py"
)
CONFIG_FILES=(
    "$DIR_DAEMONS/gps-daemon.conf"
    "$DIR_DAEMONS/obd-daemon.conf"
    "$DIR_DAEMONS/mpd-daemon.conf"
    "$DIR_DAEMONS/net-daemon.conf"
)

# ## Step 1: Install Dependencies
setStatus "Step 1: Installing dependencies..." 0
# TODO: Install dependencies here

# ## Step 2: Installing Resources
setStatus "Step 2: Installing resources..." 0
# TODO: Copy files here

# ## Step 3: Installing executables
setStatus "Step 3: Installing daemon executables..." 0
# TODO: Copy files here

# ## Step 4: Preparing executables
setStatus "Step 4: Installing daemon executables..." 0
# TODO: Copy files here

# ## Step 5: Additional Steps
# TODO: Do whatever else is necessary

# ## Setup completed
setStatus "Setup completed" 100
sleep 2

echo " ======== Script has ended ======== "
exit 0
