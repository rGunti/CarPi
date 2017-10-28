#!/usr/bin/env bash
FILE_NAME=$1
echo "Dumping GPS NMEA Log to $FILE_NAME (press Ctrl-C to stop) ..."
gpspipe -o $FILE_NAME -r -v
