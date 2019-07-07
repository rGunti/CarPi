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
    cp -f "$2" "$1"
}

# Copy array of files $1 to $2 with a given Status text $3
function copyFileArray {
    declare -a files=("${!1}")
    fileCount=${#files[@]}
    c=0

    for (( i=0; i<${fileCount}; i++ ));
    do
        setStatus "$3\n$(basename ${files[i]})" $(awk "BEGIN {printf \"%.0f\n\", $i / $fileCount * 100}")
        copyFile "$2" "${files[i]}"
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
pip install geopy >> "/var/log/carpi/install.daemons.log"

# ## Step 2: Installing Resources
setStatus "Step 2: Installing resources..." 0
copyFileArray RES_FILES[@] "$INSTALL_DESTINATION" "Step 2: Installing resources..."

# ## Step 3: Installing daemon executables
setStatus "Step 3: Installing daemon executables..." 0
copyFileArray DAEMON_FILES[@] "$INSTALL_DESTINATION" "Step 3: Installing daemon executables..."

# ## Step 4: Preparing daemon executables
setStatus "Step 4: Preparing daemon executables..." 0
for i in ${DAEMON_FILES[@]}; do
    chmod +x "${i}"
done

# ## Step 5: Registering daemons
# Step 5.1: GPS
if [ ! -f "/etc/systemd/system/carpi-gps-daemon.service" ]; then
    setStatus "Step 5: Registering daemons in OS...\n1/4: GPS Daemon" 0
    cat << EOF > /etc/systemd/system/carpi-gps-daemon.service
[Unit]
Description=CarPi GPS Daemon

[Service]
Type=simple
ExecStart=$INSTALL_DESTINATION/GpsDaemon.py

[Install]
WantedBy=multi-user.target

EOF
    systemctl daemon-reload
    systemctl disable carpi-gps-daemon
fi

# Step 5.2: OBD
if [ ! -f "/etc/systemd/system/carpi-obd-daemon.service" ]; then
    setStatus "Step 5: Registering daemons in OS...\n2/4: OBD Daemon" 25
    cat << EOF > /etc/systemd/system/carpi-obd-daemon.service
[Unit]
Description=CarPi OBD2 Daemon

[Service]
Type=simple
ExecStart=$INSTALL_DESTINATION/Obd2Daemon.py

[Install]
WantedBy=multi-user.target

EOF
    systemctl daemon-reload
    systemctl disable carpi-gps-daemon
fi

# Step 5.3: MPD
if [ ! -f "/etc/systemd/system/carpi-mpd-daemon.service" ]; then
    setStatus "Step 5: Registering daemons in OS...\n3/4: MPD Daemon" 50
    cat << EOF > /etc/systemd/system/carpi-mpd-daemon.service
[Unit]
Description=CarPi MPD Data & Control Daemon

[Service]
Type=simple
ExecStart=$INSTALL_DESTINATION/MpdDataAndControlDaemon.py

[Install]
WantedBy=multi-user.target

EOF
    systemctl daemon-reload
    systemctl disable carpi-gps-daemon
fi

# Step 5.4: MPD
if [ ! -f "/etc/systemd/system/carpi-net-daemon.service" ]; then
    setStatus "Step 5: Registering daemons in OS...\n4/4: Networking Daemon" 75
    cat << EOF > /etc/systemd/system/carpi-net-daemon.service
[Unit]
Description=CarPi Network Info Daemon

[Service]
Type=simple
ExecStart=$INSTALL_DESTINATION/NetworkInfoDaemon.py

[Install]
WantedBy=multi-user.target

EOF
    systemctl daemon-reload
    systemctl disable carpi-gps-daemon
fi

# ## Step 6: Copying Configuration Files
setStatus "Step 6: Copying Configuration Files..." 0
if [ ! -d "$CONFIG_DESTINATION" ]; then
    mkdir -p "$CONFIG_DESTINATION"
fi
for i in ${CONFIG_FILES[@]}; do
    configBaseName=$(basename "${i}")
    if [ ! -f "$CONFIG_DESTINATION/$configBaseName" ]; then
        copyFile "$CONFIG_DESTINATION" "${i}"
    else
        copyFile "$CONFIG_DESTINATION/$configBaseName.template" "${i}"
    fi
done

# ## Setup completed
setStatus "Setup completed, Daemons installed" 100
sleep 2

echo " ======== Script has ended ======== "
exit 0
