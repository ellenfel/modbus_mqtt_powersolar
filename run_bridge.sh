#!/bin/bash

# Directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Install required packages if needed
pip install pymodbus paho-mqtt pyyaml

# Run the ModbusMQTTBridge script with the config file
python "$SCRIPT_DIR/modbus_mqtt_bridge.py" "$SCRIPT_DIR/config.yaml"