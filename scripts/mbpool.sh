#!/bin/bash

# This script is used to test the Modbus TCP connection to a device.
mbpoll -m tcp -r 1 -c 5 -p 502 192.168.1.100

