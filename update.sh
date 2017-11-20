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

SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "[*] Preparing for update ..."
cd "$SCRIPT_LOCATION"
git reset --hard HEAD
git clean -xffd

echo "[*] Updating installation ..."
git pull

echo "[*] Making Scripts executable ..."
chmod +x "$SCRIPT_LOCATION/*.sh"
chmod +x "$SCRIPT_LOCATION/CarPiDaemons/*.sh"
chmod +x "$SCRIPT_LOCATION/CarPiUI/*.sh"
chmod +x "$SCRIPT_LOCATION/installer/daemons/*.sh"
chmod +x "$SCRIPT_LOCATION/installer/ui/*.sh"

echo "[O] Update has been completed. Rerun any installer scripts to update"
echo "    your components"

echo " ======== Script has ended ======== "
