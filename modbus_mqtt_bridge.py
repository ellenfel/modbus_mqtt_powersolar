import json
import time
import logging
import signal
import os
import sys
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union, Callable
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import paho.mqtt.client as mqtt
import yaml
import socket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("modbus_bridge.log")
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ModbusConfig:
    host: str
    port: int = 502
    unit_id: int = 1
    timeout: int = 5
    retries: int = 3
    retry_delay: int = 1

@dataclass
class MQTTConfig:
    broker: str
    port: int = 1883
    topic: str = "modbus/data"
    qos: int = 1
    retain: bool = False
    client_id: str = ""
    username: str = ""
    password: str = ""
    tls: bool = False
    
    def __post_init__(self):
        if not self.client_id:
            self.client_id = f"modbus-bridge-{socket.gethostname()}-{os.getpid()}"

@dataclass
class RegisterDefinition:
    name: str
    address: int
    count: int = 1
    scale: float = 1.0
    unit: str = ''
    data_type: str = 'int16'  # Options: int16, uint16, int32, uint32, float32
    byte_order: str = 'big'   # Options: big, little
    
    def __post_init__(self):
        # Convert from user-friendly 4XXXX addressing to 0-based addressing used by pymodbus
        if self.address >= 40001:
            self.address -= 40001

@dataclass
class AppConfig:
    modbus: ModbusConfig
    mqtt: MQTTConfig
    registers: List[RegisterDefinition]
    loop_interval: int = 10   # seconds
    reconnect_interval: int = 30  # seconds
    health_check_interval: int = 60  # seconds
    json_file: str = "modbus_data.json"

class ModbusMQTTBridge:
    def __init__(self, config: AppConfig):
        self.config = config
        self._modbus_client: Optional[ModbusTcpClient] = None
        
        # Use MQTTv311 instead of MQTTv5 to avoid callback issues
        self._mqtt_client = mqtt.Client(client_id=config.mqtt.client_id, 
                                    protocol=mqtt.MQTTv311)
        
        self._running = False
        self._last_reconnect_attempt = 0
        self._last_health_check = 0
        self._loop_count = 0
        
        # Configure MQTT client
        self._mqtt_client.on_connect = self._on_mqtt_connect
        self._mqtt_client.on_disconnect = self._on_mqtt_disconnect
        
        # Set MQTT credentials if provided
        if config.mqtt.username:
            self._mqtt_client.username_pw_set(config.mqtt.username, config.mqtt.password)
            
        # Enable TLS if configured
        if config.mqtt.tls:
            self._mqtt_client.tls_set()

    def _connect_modbus(self) -> bool:
        """Connect to Modbus device with retries"""
        for attempt in range(self.config.modbus.retries):
            try:
                if self._modbus_client and self._modbus_client.connected:
                    self._modbus_client.close()
                
                self._modbus_client = ModbusTcpClient(
                    self.config.modbus.host,
                    port=self.config.modbus.port,
                    timeout=self.config.modbus.timeout
                )
                
                if self._modbus_client.connect():
                    logger.info("Connected to Modbus device at %s:%d", 
                              self.config.modbus.host, self.config.modbus.port)
                    return True
                else:
                    logger.error("Failed to connect to Modbus device (attempt %d/%d)",
                               attempt+1, self.config.modbus.retries)
            except Exception as e:
                logger.error("Modbus connection attempt %d/%d failed: %s", 
                           attempt+1, self.config.modbus.retries, e)
                
            if attempt < self.config.modbus.retries - 1:
                time.sleep(self.config.modbus.retry_delay)
                
        return False

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker at %s:%d", 
                      self.config.mqtt.broker, self.config.mqtt.port)
        else:
            rc_messages = {
                1: "incorrect protocol version",
                2: "invalid client identifier",
                3: "server unavailable",
                4: "bad username or password",
                5: "not authorized"
            }
            error_msg = rc_messages.get(rc, f"unknown error (code {rc})")
            logger.error("MQTT connection failed: %s", error_msg)

    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        if rc == 0:
            logger.info("Disconnected from MQTT broker (clean)")
        else:
            logger.warning("Unexpected disconnect from MQTT broker (rc=%d)", rc)

    def _process_register_value(self, reg: RegisterDefinition, registers: List[int]) -> Union[float, List[float], str]:
        """Process register values based on data type and byte order"""
        if not registers:
            return "error"
            
        try:
            # Handle single register case
            if reg.count == 1:
                value = registers[0] * reg.scale
                return value
                
            # Handle multi-register cases
            if reg.data_type == 'int32' or reg.data_type == 'uint32':
                if reg.byte_order == 'big':
                    value = (registers[0] << 16) + registers[1]
                else:
                    value = (registers[1] << 16) + registers[0]
                    
                # Handle signed integers
                if reg.data_type == 'int32' and value > 0x7FFFFFFF:
                    value -= 0x100000000
                    
                return value * reg.scale
                
            elif reg.data_type == 'float32' and len(registers) >= 2:
                import struct
                if reg.byte_order == 'big':
                    bytes_val = struct.pack('>HH', registers[0], registers[1])
                else:
                    bytes_val = struct.pack('<HH', registers[0], registers[1])
                    
                value = struct.unpack('>f', bytes_val)[0]
                return value * reg.scale
                
            # Default case: return scaled list
            return [v * reg.scale for v in registers]
            
        except Exception as e:
            logger.exception("Error processing register value: %s", e)
            return "error"

    def _read_registers(self) -> Dict[str, Any]:
        """Read all configured registers with error handling"""
        results = {
            "timestamp": time.time(), 
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
            "loop_count": self._loop_count,
            "data": {}
        }
        
        if not self._modbus_client or not self._modbus_client.connected:
            logger.error("Modbus client not connected")
            return results

        for reg in self.config.registers:
            try:
                # Set the slave ID before reading
                self._modbus_client.unit_id = self.config.modbus.unit_id
                
                # Debug log the actual address being used
                logger.debug("Reading register %s at address %d (original address %d)", 
                           reg.name, reg.address, reg.address + 40001)
                
                response = self._modbus_client.read_holding_registers(
                    reg.address,
                    count=reg.count
                )
                
                if response.isError():
                    logger.warning("Error response reading %s (address %d): %s", 
                                reg.name, reg.address + 40001, response)
                    value = "error"
                else:
                    value = self._process_register_value(reg, response.registers)
                    
                results["data"][reg.name] = {
                    "value": value,
                    "unit": reg.unit,
                    "address": reg.address + 40001  # Convert back to user-friendly address for logging
                }
                
            except ModbusException as e:
                logger.error("Modbus error reading %s (address %d): %s", 
                        reg.name, reg.address + 40001, e)
                results["data"][reg.name] = {
                    "value": "error",
                    "unit": reg.unit,
                    "address": reg.address + 40001,
                    "error": str(e)
                }
            except Exception as e:
                logger.exception("Unexpected error reading %s (address %d)", 
                            reg.name, reg.address + 40001)
                results["data"][reg.name] = {
                    "value": "error",
                    "unit": reg.unit,
                    "address": reg.address + 40001,
                    "error": str(e)
                }

        return results

    def _save_to_json(self, data: Dict[str, Any]) -> bool:
        """Save data to JSON file"""
        try:
            with open(self.config.json_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("Data saved to %s", self.config.json_file)
            return True
        except Exception as e:
            logger.error("Failed to save data to JSON file: %s", e)
            return False

    def _publish_data(self, data: Dict) -> bool:
        """Publish data to MQTT with QoS handling"""
        if not self._mqtt_client.is_connected():
            logger.warning("MQTT client not connected, cannot publish")
            return False
            
        try:
            payload = json.dumps(data)
            result = self._mqtt_client.publish(
                self.config.mqtt.topic,
                payload=payload,
                qos=self.config.mqtt.qos,
                retain=self.config.mqtt.retain
            )
            
            # Wait for publish to complete with a reasonable timeout
            if not result.is_published():
                result.wait_for_publish(timeout=5)
                
            if result.rc == 0:
                logger.debug("Data published to MQTT topic %s", self.config.mqtt.topic)
                return True
            else:
                logger.warning("MQTT publish failed (rc=%d)", result.rc)
                return False
        except Exception as e:
            logger.error("MQTT publish failed: %s", e)
            return False

    def _clear_json_file(self) -> None:
        """Clear JSON file after successful MQTT publishing"""
        try:
            open(self.config.json_file, 'w').close()
            logger.debug("Cleared JSON file contents")
        except Exception as e:
            logger.error("Failed to clear JSON file: %s", e)

    def _check_connections(self) -> None:
        """Check and restore connections if needed"""
        now = time.monotonic()
        
        # Only attempt reconnections at the specified interval
        if now - self._last_reconnect_attempt < self.config.reconnect_interval:
            return
            
        self._last_reconnect_attempt = now
        
        # Check Modbus connection
        if not self._modbus_client or not self._modbus_client.connected:
            logger.info("Attempting to reconnect to Modbus...")
            self._connect_modbus()
            
        # Check MQTT connection
        if not self._mqtt_client.is_connected():
            logger.info("Attempting to reconnect to MQTT broker...")
            try:
                self._mqtt_client.reconnect()
            except Exception as e:
                logger.error("MQTT reconnection failed: %s", e)

    def _perform_health_check(self) -> None:
        """Perform periodic health check"""
        now = time.monotonic()
        
        # Only run health check at the specified interval
        if now - self._last_health_check < self.config.health_check_interval:
            return
            
        self._last_health_check = now
        
        # Basic health check implementation
        logger.info("Health check: Modbus connected: %s, MQTT connected: %s", 
                  bool(self._modbus_client and self._modbus_client.connected),
                  self._mqtt_client.is_connected())

    def run(self):
        """Main execution loop"""
        self._running = True
        self._loop_count = 0
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Initial connections
        modbus_connected = self._connect_modbus()
        if not modbus_connected:
            logger.warning("Initial Modbus connection failed, will retry in loop")

        try:
            # Connect to MQTT broker
            try:
                logger.info("Attempting to connect to MQTT broker at %s:%d", 
                        self.config.mqtt.broker, self.config.mqtt.port)
                self._mqtt_client.connect(
                    self.config.mqtt.broker,
                    port=self.config.mqtt.port,
                    keepalive=60
                )
                self._mqtt_client.loop_start()
                logger.info("MQTT connection initiated")
            except Exception as e:
                logger.error("Initial MQTT connection failed: %s", e)

            while self._running:
                start_time = time.monotonic()
                self._loop_count += 1
                
                logger.info("Starting loop %d", self._loop_count)
                
                # Check connections
                self._check_connections()
                
                # Periodic health check
                self._perform_health_check()
                
                # Read registers and process data
                data = self._read_registers()
                
                # Save to JSON
                json_saved = self._save_to_json(data)
                
                # Publish to MQTT if JSON was saved successfully
                if json_saved:
                    mqtt_published = self._publish_data(data)
                    
                    # Clear JSON file after successful MQTT publish
                    if mqtt_published:
                        self._clear_json_file()
                
                logger.info("Loop %d done", self._loop_count)
                
                # Maintain consistent loop timing
                elapsed = time.monotonic() - start_time
                if elapsed < self.config.loop_interval:
                    time.sleep(self.config.loop_interval - elapsed)
                else:
                    logger.warning("Loop iteration overrun by %.2f seconds", elapsed - self.config.loop_interval)

        except Exception as e:
            logger.exception("Unexpected error in main loop: %s", e)
        finally:
            self.shutdown()

    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        logger.info("Received signal %d, shutting down...", signum)
        self._running = False

    def shutdown(self):
        """Cleanup resources"""
        logger.info("Shutting down services...")
        
        # Close Modbus connection
        if self._modbus_client and self._modbus_client.connected:
            try:
                self._modbus_client.close()
                logger.info("Modbus connection closed")
            except Exception as e:
                logger.error("Error closing Modbus connection: %s", e)

        # Close MQTT connection
        try:
            self._mqtt_client.loop_stop()
            self._mqtt_client.disconnect()
            logger.info("MQTT connection closed")
        except Exception as e:
            logger.error("Error closing MQTT connection: %s", e)

def load_config(config_file=None):
    """Load configuration from file or use defaults"""
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
                    
            # Create config objects from loaded data
            modbus_config = ModbusConfig(**config_data.get('modbus', {}))
            mqtt_config = MQTTConfig(**config_data.get('mqtt', {}))
            
            # Convert register dictionaries to RegisterDefinition objects
            registers = []
            for reg_data in config_data.get('registers', []):
                registers.append(RegisterDefinition(**reg_data))
                
            # Create main config
            main_config = {k: v for k, v in config_data.items() 
                          if k not in ('modbus', 'mqtt', 'registers')}
            
            return AppConfig(
                modbus=modbus_config,
                mqtt=mqtt_config,
                registers=registers,
                **main_config
            )
        except Exception as e:
            logger.error("Error loading config from %s: %s", config_file, e)
            
    # Default config if loading fails or no file specified
    return AppConfig(
        modbus=ModbusConfig(
            host="192.168.1.100",
            unit_id=1
        ),
        mqtt=MQTTConfig(
            broker="192.168.1.200",
            topic="modbus/data"
        ),
        registers=[
            RegisterDefinition("Temperature", 40001, unit="°C", scale=0.1),
            RegisterDefinition("Voltage", 40002, unit="V", scale=0.01),
            RegisterDefinition("Power", 40003, count=2, unit="kW")
        ]
    )

if __name__ == "__main__":
    # Check for config file argument
    config_file = None
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        
    # Load configuration
    config = load_config(config_file)
    
    # Create and run the bridge
    bridge = ModbusMQTTBridge(config)
    bridge.run()