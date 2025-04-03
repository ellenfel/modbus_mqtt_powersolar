#!/bin/bash
# A script to scan common subnets for a device (such as a Modbus inverter)
# using both a ping sweep and an nmap port scan for port 502.

# Define a list of common IP subnets to scan.
subnets=(
#  "192.168.0.0/24"
  "192.168.1.0/24"
#  "192.168.2.0/24"
#  "10.0.0.0/24"
#  "10.0.1.0/24"
)

for subnet in "${subnets[@]}"; do
    echo "====================================="
    echo "Scanning subnet: $subnet"
    echo "-------------------------------------"
    
    # Ping sweep to list active hosts
    echo "[*] Performing ping sweep on $subnet:"
    nmap -sn "$subnet" | grep "Nmap scan report"
    
    # Scan for open Modbus TCP port (502)
    echo ""
    echo "[*] Scanning for open port 502 (Modbus TCP) on $subnet:"
    nmap -p502 "$subnet" | grep "502/tcp" -A 2
    echo ""
done

echo "Scan complete."
