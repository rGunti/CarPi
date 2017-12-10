# Auto-Installer
This folder contains auto-installer scripts designed to be run by the Maintenance Mode Updater

## How to create an auto-installer script?
Copy the `skeleton.sh` script and begin writing the installation script.
Remember to `exit 0` on success or with another code in case of failure.
Report progress by using the provided output function. This text will then 
be visible in a Gauge Box.

For all non-zero error codes, provide error messages as `autoscript_{ErrorCodeHere}.msg`.
