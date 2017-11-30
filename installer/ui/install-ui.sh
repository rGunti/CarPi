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

function copyDir {
    DESTINATION=$1
    SOURCE=$2

    echo "    Copying $(basename "$SOURCE") ..."
    cp -rf "$SOURCE" "$DESTINATION"
}

SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

INSTALL_SOURCE="$SCRIPT_LOCATION/../../"
INSTALL_DESTINATION="/usr/bin/carpi/"
CONFIG_DESTINATION="/etc/carpi/"
CONFIG_FILE_DESTINATION="/etc/carpi/ui.conf"

DIR_COMMONS="$INSTALL_SOURCE/CarPiCommons"
DIR_UI="$INSTALL_SOURCE/CarPiUI"

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

cat << EOF
 ========== CarPi UI Installer ==========
This script install the following scripts:
 - CarPi UI App (CarPiUI.py)

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

echo "[*] Installing Python Dependencies ..."
pip install pygame
pip install numpy

echo "[*] Installing CarPi Commons ..."
copyFile "$INSTALL_DESTINATION" "$DIR_COMMONS/CarPiConfig.py"

echo "[*] Installing UI Dependencies ..."
copyFile "$INSTALL_DESTINATION" "$DIR_UI/pqGUI.py"
copyFile "$INSTALL_DESTINATION" "$DIR_UI/PygameUtils.py"

echo "[*] Installing UI App ..."
copyFile "$INSTALL_DESTINATION" "$DIR_UI/CarPiUI.py"
copyFile "$INSTALL_DESTINATION" "$DIR_UI/CarPiUIApp.py"
copyFile "$INSTALL_DESTINATION" "$DIR_UI/CarPiSettingsWindows.py"
copyFile "$INSTALL_DESTINATION" "$DIR_UI/carpi-ui.sh"

echo "[*] Installing Resources ..."
copyDir "$INSTALL_DESTINATION" "$DIR_UI/res"

echo "[*] Preparing Files ..."
chmod +x "$DIR_UI/carpi-ui.sh"

echo "[*] Checking for configuration files ..."
if [ ! -d "$CONFIG_DESTINATION" ]; then
    echo "[*] Creating Configuration directory ..."
    mkdir -p "$CONFIG_DESTINATION"
fi
if [ ! -f "$CONFIG_FILE_DESTINATION" ]; then
    copyFile "$CONFIG_DESTINATION" "$DIR_UI/ui.conf"
else
    copyFile "$CONFIG_FILE_DESTINATION.template" "$DIR_UI/ui.conf"
fi

echo ""
echo "[O] Installation has been completed successfully!"
echo " =========== Script has ended =========== "
