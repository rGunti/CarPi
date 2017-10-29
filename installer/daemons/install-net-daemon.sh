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

function copyFile {
    DESTINATION=$1
    SOURCE=$2

    echo "    Copying $(basename "$SOURCE") ..."
    cp -f "$SOURCE" "$DESTINATION"
}

SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

INSTALL_SOURCE="$SCRIPT_LOCATION/../../"
INSTALL_DESTINATION="/usr/bin/carpi/"
CONFIG_DESTINATION="/etc/carpi/"
CONFIG_FILE_DESTINATION="/etc/carpi/net-daemon.conf"

DIR_COMMONS="$INSTALL_SOURCE/CarPiCommons"
DIR_DAEMONS="$INSTALL_SOURCE/CarPiDaemons"

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

cat << EOF
 ========== CarPi Daemon Installer ==========
This script install the following Daemons:
 - Network Info Daemon (NetworkInfoDaemon.py)

Any existing installations will be replaced though configuration files will be left
alone. You will receive an updated template configuration.

The installation will take place in the following directory:
$INSTALL_DESTINATION

EOF

cat << EOF
This software is distributed under the MIT License:

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
EOF

echo -n "[?] Do you accept this license? [Y/N] "
read -n 1 license_agree
echo ""

case $license_agree in
[Yy])
    echo "[*] Please wait while the installation starts ..."
    ;;
*)
    echo "[*] Quitting installer ..."
    echo " =========== Script has ended =========== "
    exit 1
    ;;
esac

if [ ! -d "$INSTALL_DESTINATION" ]; then
    echo "[*] Creating destination directory ..."
    mkdir -p "$INSTALL_DESTINATION"
fi

echo "[*] Installing CarPi Commons ..."
copyFile "$INSTALL_DESTINATION" "$DIR_COMMONS/CarPiConfig.py"
copyFile "$INSTALL_DESTINATION" "$DIR_COMMONS/CarPiLogging.py"
copyFile "$INSTALL_DESTINATION" "$DIR_COMMONS/CarPiThreading.py"
copyFile "$INSTALL_DESTINATION" "$DIR_COMMONS/RedisKeys.py"
copyFile "$INSTALL_DESTINATION" "$DIR_COMMONS/RedisUtils.py"

echo "[*] Installing Daemons ..."
copyFile "$INSTALL_DESTINATION" "$DIR_DAEMONS/NetworkInfoDaemon.py"
chmod +x "$INSTALL_DESTINATION/NetworkInfoDaemon.py"

echo "[*] Cleaning up ..."


echo "[*] Checking for configuration files ..."
if [ ! -d "$CONFIG_DESTINATION" ]; then
    echo "[*] Creating Configuration directory ..."
    mkdir -p "$CONFIG_DESTINATION"
fi
if [ ! -f "$CONFIG_FILE_DESTINATION" ]; then
    copyFile "$CONFIG_DESTINATION" "$DIR_DAEMONS/net-daemon.conf"
else
    copyFile "$CONFIG_FILE_DESTINATION.template" "$DIR_DAEMONS/net-daemon.conf"
fi

echo ""
echo "[O] Installation has been completed!"
echo -n "[?] Do you want to setup the daemon as a service? [Y/N] "
read -n 1 daemon_setup
echo ""

case $daemon_setup in
[Yy])
    echo "[*] Setting up a Daemon for you ..."
    cat << EOF > /etc/systemd/system/carpi-net-daemon.service
[Unit]
Description=CarPi Network Info Daemon

[Service]
Type=simple
ExecStart=$INSTALL_DESTINATION/NetworkInfoDaemon.py

[Install]
WantedBy=multi-user.target

EOF
    systemctl enable carpi-net-daemon
    systemctl start carpi-net-daemon
    ;;
esac

echo "[O] Installation has been completed successfully!"
echo " =========== Script has ended =========== "
