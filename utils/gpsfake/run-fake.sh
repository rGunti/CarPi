#!/usr/bin/env bash
FILE_NAME=$1

echo "Shutting down GPSD before starting fakegps ..."
sudo service gpsd stop

echo "Starting gpsfake with $FILE_NAME (press Ctrl-C to stop) ..."
gpsfake -c 0.1 $FILE_NAME

echo "Restarting GPSD ..."
sudo service gpsd start

echo " ======== Script has ended ======== "
