#!/bin/bash
# Simple Modbus test script for inverter
# Usage: ./modbus_test.sh <ip_address> [slave_id]

# Check if IP address is provided
if [ -z "$1" ]; then
    echo "Error: IP address required"
    echo "Usage: ./modbus_test.sh <ip_address> [slave_id]"
    exit 1
fi

# Set IP address from first argument
IP_ADDRESS="$1"

# Set slave ID (default to 1 if not provided)
SLAVE_ID="${2:-1}"

# Function to read registers and display results
read_registers() {
    local register=$1
    local count=$2
    local description=$3
    
    echo "Reading $description (Register: $register, Count: $count)..."
    mbpoll -a "$SLAVE_ID" -t 4 -r "$register" -c "$count" "$IP_ADDRESS"
    echo "----------------------------------------"
}

echo "===== Inverter Modbus Test ====="
echo "IP Address: $IP_ADDRESS"
echo "Slave ID: $SLAVE_ID"
echo "----------------------------------------"

# Read different register groups - modify these based on your inverter's register map
read_registers 1 4 "Basic Parameters"
read_registers 100 4 "Power Values"
read_registers 200 6 "Status Information"
read_registers 300 4 "Temperature Data"

echo "Modbus test completed"