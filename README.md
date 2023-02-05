# HP Switch Controller
Connect to HP switches through SSH and extract Interfaces table with IP addresses and MAC address in Excel format.

## How to use

First, setup the range for your local network in line 211. 
Please wait a little bit till the function complete getting the mac addresses that have each IP in the specified the range.

Next, register the switches you'd like to control then you'll get a menu with commands. Choose by number.

Running command 2 will generate an excel file of a list of devices connected to the chosen switch with details.
## Execution

Simply double click on the file after added your LAN Range.

This script installs the necessary packages by itself.
In case of an error, delete lines 1-11 and try installing the packages by yourself using pip.
