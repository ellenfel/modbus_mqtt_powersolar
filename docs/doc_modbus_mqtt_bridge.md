# ModbusMQTTBridge Documentation

## Overview

ModbusMQTTBridge is a Python application that establishes a bridge between Modbus TCP devices and MQTT brokers. It reads data from Modbus registers at configurable intervals, saves the data to a JSON file, and publishes it to an MQTT topic. This bridge is designed for industrial IoT applications, allowing data from legacy Modbus equipment to be integrated into modern IoT systems.

## Features

- **Modbus TCP Communication**: Reads holding registers from Modbus TCP devices
- **MQTT Integration**: Publishes data to configurable MQTT topics with QoS and retain support
- **Data Processing**: Processes register values based on data type and scaling factors
- **Data Persistence**: Saves readings to a local JSON file
- **Error Handling**: Comprehensive error handling and automatic reconnection
- **Type Handling**: Support for different data types (int16, uint16, int32, uint32, float32)
- **Configurable**: External configuration via YAML or JSON files
- **Security**: Support for MQTT authentication and TLS encryption
- **Monitoring**: Health checks and connection monitoring
- **Graceful Shutdown**: Proper handling of system signals for clean termination

## Requirements

- Python 3.6 or higher
- Dependencies:
  - pymodbus
  - paho-mqtt
  - pyyaml (for YAML configuration support)

## Installation

1. Clone or download the script to your local machine
2. Install required dependencies:

```bash
pip install pymodbus paho-mqtt pyyaml
```

## Configuration

The bridge is configured through a YAML or JSON file. A sample configuration file structure is shown below:

```yaml
# Modbus Connection Settings
modbus:
  host: "192.168.1.100"  # IP address of the Modbus device
  port: 502              # Default Modbus TCP port
  unit_id: 1             # Modbus unit/slave ID
  timeout: 5             # Connection timeout in seconds
  retries: 3             # Number of connection retry attempts
  retry_delay: 2         # Delay between retries in seconds

# MQTT Connection Settings
mqtt:
  broker: "192.168.1.200"  # IP address of the MQTT broker
  port: 1883               # Default MQTT port
  topic: "device/modbus"   # Topic to publish data
  qos: 1                   # Quality of Service (0, 1, or 2)
  retain: false            # Whether to retain messages on the broker
  client_id: "modbus-bridge-1"  # Client ID (leave empty for auto-generated)
  username: "mqtt_user"    # MQTT username (optional)
  password: "mqtt_pass"    # MQTT password (optional)
  tls: false               # Whether to use TLS/SSL

# Register Definitions
registers:
  - name: "Temperature"
    address: 40001
    count: 1
    scale: 0.1
    unit: "°C"
    data_type: "int16"
    byte_order: "big"
  
  - name: "Power"
    address: 40003
    count: 2
    scale: 0.001
    unit: "kW"
    data_type: "int32"
    byte_order: "big"

# Application Settings
loop_interval: 10            # Time between data readings in seconds
reconnect_interval: 30       # Time between reconnection attempts in seconds
health_check_interval: 60    # Time between health checks in seconds
json_file: "modbus_data.json"  # File to store the latest readings
```

### Configuration Details

#### Modbus Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| host | IP address or hostname of the Modbus device | Required |
| port | TCP port number | 502 |
| unit_id | Modbus unit/slave ID | 1 |
| timeout | Connection timeout in seconds | 5 |
| retries | Number of connection retries | 3 |
| retry_delay | Delay between retries in seconds | 1 |

#### MQTT Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| broker | IP address or hostname of MQTT broker | Required |
| port | MQTT port number | 1883 |
| topic | Topic for publishing data | "modbus/data" |
| qos | Quality of Service (0, 1, or 2) | 1 |
| retain | Whether to retain messages | false |
| client_id | Client identifier | Auto-generated |
| username | Authentication username | Empty |
| password | Authentication password | Empty |
| tls | Whether to use TLS/SSL | false |

#### Register Definition

| Parameter | Description | Default |
|-----------|-------------|---------|
| name | Human-readable name for the register | Required |
| address | Modbus register address | Required |
| count | Number of registers to read | 1 |
| scale | Scaling factor for the value | 1.0 |
| unit | Unit of measurement | Empty |
| data_type | Data type (int16, uint16, int32, uint32, float32) | "int16" |
| byte_order | Byte order (big, little) | "big" |

#### Application Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| loop_interval | Time between data readings in seconds | 10 |
| reconnect_interval | Time between reconnection attempts in seconds | 30 |
| health_check_interval | Time between health checks in seconds | 60 |
| json_file | File path for JSON data storage | "modbus_data.json" |

## Usage

Run the script with a configuration file:

```bash
python modbus_mqtt_bridge.py config.yaml
```

If no configuration file is specified, the script will use default settings.

## JSON Output Format

The bridge produces JSON data in the following format:

```json
{
  "timestamp": 1712169542.653,
  "datetime": "2025-04-03 12:32:22",
  "loop_count": 5,
  "data": {
    "Temperature": {
      "value": 25.3,
      "unit": "°C",
      "address": 40001
    },
    "Voltage": {
      "value": 232.45,
      "unit": "V",
      "address": 40002
    },
    "Power": {
      "value": 4.127,
      "unit": "kW",
      "address": 40003
    },
    "Current": {
      "value": "error",
      "unit": "A",
      "address": 40005,
      "error": "Modbus error: No response received"
    }
  }
}
```

## Operation Details

### Startup Sequence

1. Load configuration from the specified file
2. Establish initial connections to Modbus device and MQTT broker
3. Start the main polling loop

### Main Loop

1. Check connections and reconnect if necessary
2. Perform periodic health checks
3. Read all configured Modbus registers
4. Process the values based on data types and scaling factors
5. Save the data to a JSON file
6. Publish the data to the MQTT topic
7. Clear the JSON file after successful publishing
8. Wait for the configured interval
9. Repeat

### Error Handling

- Connection failures trigger automatic reconnection attempts
- Register read errors are recorded in the output data
- All exceptions are caught, logged, and handled gracefully
- The loop continues running despite temporary failures

### Shutdown

The script handles the following signals for graceful shutdown:
- SIGINT (Ctrl+C)
- SIGTERM (termination signal)

During shutdown, all connections are properly closed and resources are released.

## Data Types

The script supports the following data types for Modbus registers:

| Data Type | Description | Registers Used |
|-----------|-------------|---------------|
| int16 | 16-bit signed integer | 1 |
| uint16 | 16-bit unsigned integer | 1 |
| int32 | 32-bit signed integer | 2 |
| uint32 | 32-bit unsigned integer | 2 |
| float32 | 32-bit floating point | 2 |

## Logging

The script logs information to both the console and a log file (`modbus_bridge.log`). Log entries include:
- Connection status
- Register read operations
- MQTT publish status
- Errors and exceptions
- Health check status

## Error Codes

### MQTT Connection Error Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Incorrect protocol version |
| 2 | Invalid client identifier |
| 3 | Server unavailable |
| 4 | Bad username or password |
| 5 | Not authorized |

## Advanced Usage

### Using TLS with MQTT

To secure MQTT communications with TLS:

1. Set `tls: true` in the MQTT configuration
2. Place CA certificates in the default location or configure paths in the code

### Custom Data Processing

For custom data processing, modify the `_process_register_value` method to implement custom logic for specific register types.

### Integration with Other Systems

The bridge can be extended to:
- Store data in databases by modifying the data persistence logic
- Send alerts based on threshold values
- Integrate with other messaging systems

## Troubleshooting

### Common Issues

1. **Modbus Connection Failures**
   - Check IP address and port number
   - Verify the device is powered on and accessible
   - Check for firewall rules blocking port 502

2. **MQTT Connection Issues**
   - Verify broker address and port
   - Check authentication credentials
   - Ensure the client ID is unique on the broker

3. **Data Type Errors**
   - Verify the register addresses match your device's documentation
   - Check that the data_type and byte_order settings match your device

### Debugging

For more detailed logging, modify the log level in the script:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("modbus_bridge.log")
    ]
)
```

## License

This software is provided as is, without warranty of any kind.

## Contributors

This script was developed by [Your Name/Organization] and may include contributions from the community.

---

*Last updated: April 3, 2025*