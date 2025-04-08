# Modbus Inverter Simulator and MQTT Bridge

This project provides a Modbus TCP simulator for inverters and a bridge to connect Modbus devices to MQTT brokers. It's designed to help test and develop systems that interact with Modbus-enabled inverters and other devices.

## Project Structure

```
inverter/
├── src/                    # Source code files
│   ├── modbus-inverter-simulator.py  # Simulator for Modbus inverter
│   ├── modbus_mqtt_bridge.py         # Bridge between Modbus and MQTT
│   ├── simple_mqtt.py                # Simple MQTT client
│   ├── port_range_scan.py            # Network port scanner
│   └── on_production_mb_server.py    # Production Modbus server
├── config/                # Configuration files
│   ├── config.yaml       # Main configuration
│   └── inverter.yaml     # Inverter-specific settings
├── scripts/              # Shell scripts
│   ├── mbpool.sh         # Modbus pool script
│   ├── run_bridge.sh     # Bridge startup script
│   └── ip_range_scan.sh  # IP range scanner
├── docs/                 # Documentation
│   └── doc_modbus_mqtt_bridge.md  # Bridge documentation
├── logs/                 # Log files
│   ├── modbus_bridge.log
│   └── modbus_server.log
├── data/                 # Data files
│   ├── modbus_data.json
│   └── test_data.json
└── tests/               # Test files
    └── test_modbus_server.py
```

## Features

- Modbus TCP simulator for testing inverter communication
- MQTT bridge for connecting Modbus devices to MQTT brokers
- Network scanning tools for discovering Modbus devices
- Configuration management for different environments
- Comprehensive logging system
- Test suite for server functionality

## Prerequisites

- Python 3.x
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd inverter
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example configuration files in the `config/` directory
2. Modify the settings according to your environment:
   - `config.yaml`: Main configuration for the bridge
   - `inverter.yaml`: Inverter-specific settings

## Usage

### Running the Modbus Simulator

```bash
python src/modbus-inverter-simulator.py
```

### Starting the MQTT Bridge

```bash
./scripts/run_bridge.sh
```

### Scanning for Modbus Devices

```bash
./scripts/ip_range_scan.sh
```

## Logging

Log files are stored in the `logs/` directory:
- `modbus_bridge.log`: Bridge operation logs
- `modbus_server.log`: Server operation logs

## Testing

Run the test suite:
```bash
python tests/test_modbus_server.py
```

## Documentation

Detailed documentation is available in the `docs/` directory:
- `doc_modbus_mqtt_bridge.md`: Comprehensive guide for the Modbus-MQTT bridge

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


#example mbpoll
mbpoll -a 1 -t 4 -r 1 -c 4 192.168.1.100