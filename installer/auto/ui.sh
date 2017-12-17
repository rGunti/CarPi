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

# Copy a folder $2 to $1
function copyDir {
    cp -rf "$2" "$1"
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
DIR_UI="$INSTALL_SOURCE/CarPiUI"

RES_FILES=(
    "$DIR_COMMONS/CarPiConfig.py"
    "$DIR_COMMONS/CarPiLogging.py"
    "$DIR_COMMONS/CarPiThreading.py"
    "$DIR_COMMONS/CarPiUtils.py"
    "$DIR_COMMONS/RedisKeys.py"
    "$DIR_COMMONS/RedisUtils.py"
    "$DIR_UI/pqGUI.py"
    "$DIR_UI/PygameUtils.py"
)
UI_FILES=(
    "$DIR_UI/CarPiUI.py"
    "$DIR_UI/CarPiUIApp.py"
    "$DIR_UI/CarPiSettingsWindows.py"
    "$DIR_UI/CarPiStyles.py"
    "$DIR_UI/carpi-ui.sh"
)
CONFIG_FILE="$DIR_UI/ui.conf"
CONFIG_FILE_DESTINATION="/etc/carpi/ui.conf"

# ## Step 1: Install Dependencies
setStatus "Step 1: Installing dependencies..." 0
pip install pygame numpy >> "/var/log/carpi/install.ui.log"

# ## Step 2: Installing Resources
setStatus "Step 2: Installing resources..." 0
copyFileArray RES_FILES[@] "$INSTALL_DESTINATION" "Step 2: Installing resources..."

setStatus "Step 2: Installing UI resources..." 0
copyDir "$INSTALL_DESTINATION" "$DIR_UI/res"

# ## Step 3: Installing executables
setStatus "Step 3: Installing UI executables..." 0
copyFileArray UI_FILES[@] "$INSTALL_DESTINATION" "Step 3: Installing UI executables..."

# ## Step 4: Preparing executables
setStatus "Step 4: Preparing UI executables..." 0
chmod +x "$INSTALL_DESTINATION/carpi-ui.sh"

# ## Step 5: Additional Steps
setStatus "Step 5: Setting up configuration..." 0
if [ ! -d "$CONFIG_DESTINATION" ]; then
    mkdir -p "$CONFIG_DESTINATION"
fi
if [ ! -f "$CONFIG_FILE_DESTINATION" ]; then
    copyFile "$CONFIG_DESTINATION" "$CONFIG_FILE"
else
    copyFile "$CONFIG_FILE_DESTINATION.template" "$CONFIG_FILE"
fi

# ## Setup completed
setStatus "Setup completed" 100
sleep 2

echo " ======== Script has ended ======== "
exit 0
