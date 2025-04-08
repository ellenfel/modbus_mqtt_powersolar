import logging
import random
import struct
import time
import asyncio
import signal
import sys
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server import StartAsyncTcpServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("modbus_server.log")
    ]
)
logger = logging.getLogger(__name__)

# Global exit event for clean shutdown
shutdown_event = asyncio.Event()

class InverterSimulator:
    def __init__(self, update_interval=5):
        """Initialize the inverter simulator with a specified update interval."""
        self.update_interval = update_interval
        
        # Initialize data store
        self.datastore = self._setup_datastore()
        
        # Values for simulation
        self.dc_voltage = 350.0  # 350.0V
        self.dc_current = 8.5    # 8.5A
        self.ac_voltage = 230.0  # 230.0V
        self.ac_current = 7.2    # 7.2A
        self.ac_frequency = 50.0 # 50.0Hz
        self.power = 1500.0      # 1500W
        self.energy = 10000.0    # 10000Wh (10kWh)
        self.temperature = 35.0  # 35.0°C
        self.status = 1          # 1=Running
        
    def _setup_datastore(self):
        """Create and setup the Modbus datastore with appropriate register blocks."""
        # Create data blocks for different register types
        # Coils (0xxxxx) - Digital outputs
        coil_block = ModbusSequentialDataBlock(0, [0] * 100)
        
        # Discrete Inputs (1xxxxx) - Digital inputs
        discrete_block = ModbusSequentialDataBlock(0, [0] * 100)
        
        # Input Registers (3xxxxx) - Analog inputs (read-only)
        input_block = ModbusSequentialDataBlock(0, [0] * 1000)
        
        # Holding Registers (4xxxxx) - Analog outputs (read/write)
        holding_block = ModbusSequentialDataBlock(0, [0] * 1000)
        
        # Create slave context
        slave_context = ModbusSlaveContext(
            di=discrete_block,
            co=coil_block,
            ir=input_block,
            hr=holding_block
        )
        
        # Create server context with single slave
        return ModbusServerContext(slaves={1: slave_context}, single=False)
    
    def _update_registers(self):
        """Update register values with simulated inverter data."""
        # Add small random variations to simulate real changes
        self.dc_voltage += random.uniform(-5, 5)
        self.dc_voltage = max(300, min(400, self.dc_voltage))  # Keep within range
        
        self.dc_current += random.uniform(-0.5, 0.5)
        self.dc_current = max(0, min(15, self.dc_current))
        
        self.ac_voltage += random.uniform(-2, 2)
        self.ac_voltage = max(220, min(240, self.ac_voltage))
        
        self.ac_current += random.uniform(-0.3, 0.3)
        self.ac_current = max(0, min(10, self.ac_current))
        
        self.ac_frequency += random.uniform(-0.1, 0.1)
        self.ac_frequency = max(49.5, min(50.5, self.ac_frequency))
        
        self.power = self.ac_voltage * self.ac_current
        
        self.energy += self.power * (self.update_interval / 3600)  # Convert to Wh
        
        self.temperature += random.uniform(-1, 1)
        self.temperature = max(20, min(60, self.temperature))
        
        # Get the registers from context
        slave_id = 1
        context = self.datastore.slaves[slave_id]
        
        try:
            # UPDATE INPUT REGISTERS (3xxxx)
            
            # DC Voltage (uint16, scale 0.1) - Register 30001
            context.setValues(3, 0, [int(self.dc_voltage * 10)])
            
            # DC Current (uint16, scale 0.1) - Register 30003
            context.setValues(3, 2, [int(self.dc_current * 10)])
            
            # AC Output Voltage (uint16, scale 0.1) - Register 30071
            context.setValues(3, 70, [int(self.ac_voltage * 10)])
            
            # AC Output Current (uint16, scale 0.1) - Register 30073
            context.setValues(3, 72, [int(self.ac_current * 10)])
            
            # AC Output Frequency (uint16, scale 0.01) - Register 30075
            context.setValues(3, 74, [int(self.ac_frequency * 100)])
            
            # Inverter Status (uint16) - Register 30201
            context.setValues(3, 200, [self.status])
            
            # Inverter Temperature (int16, scale 0.1) - Register 30231
            temp_value = int(self.temperature * 10)
            if temp_value < 0:
                temp_value = 65536 + temp_value  # Convert to 2's complement
            context.setValues(3, 230, [temp_value])
            
            # Total Power int32 (Big Endian) - Register 30775-30776
            power_int = int(self.power)
            high_word = (power_int >> 16) & 0xFFFF
            low_word = power_int & 0xFFFF
            context.setValues(3, 774, [high_word, low_word])
            
            # Total Power int32 (Little Endian) - This is the same value in different byte order
            context.setValues(3, 776, [low_word, high_word])
            
            # Total Power as float32 (Big Endian) - Register 30779-30780
            float_bytes = struct.pack('>f', self.power)
            float_words = struct.unpack('>HH', float_bytes)
            context.setValues(3, 778, [float_words[0], float_words[1]])
            
            # Total Power as float32 (Little Endian) - This is the same value in different byte order
            float_bytes = struct.pack('<f', self.power)
            float_words = struct.unpack('<HH', float_bytes)
            context.setValues(3, 780, [float_words[0], float_words[1]])
            
            # Total Energy (uint32, scale 0.1) - Register 30513-30514
            energy_int = int(self.energy * 10)
            high_word = (energy_int >> 16) & 0xFFFF
            low_word = energy_int & 0xFFFF
            context.setValues(3, 512, [high_word, low_word])
            
            # UPDATE HOLDING REGISTERS (4xxxx)
            # Copy some of the values to holding registers for testing
            
            # DC Voltage (uint16, scale 0.1) - Register 40001
            context.setValues(4, 0, [int(self.dc_voltage * 10)])
            
            # DC Current (uint16, scale 0.1) - Register 40003
            context.setValues(4, 2, [int(self.dc_current * 10)])
            
            # AC Output Voltage (uint16, scale 0.1) - Register 40071
            context.setValues(4, 70, [int(self.ac_voltage * 10)])
            
            # Total Power int32 (Big Endian) - Register 40775-40776
            context.setValues(4, 774, [high_word, low_word])
            
            # Total Energy - Register 40513-40514
            context.setValues(4, 512, [high_word, low_word])
            
            logger.info(f"Updated registers: "
                      f"DC: {self.dc_voltage:.1f}V/{self.dc_current:.1f}A, "
                      f"AC: {self.ac_voltage:.1f}V/{self.ac_current:.1f}A/{self.ac_frequency:.2f}Hz, "
                      f"Power: {self.power:.1f}W, Energy: {self.energy/1000:.2f}kWh, "
                      f"Temp: {self.temperature:.1f}°C")
                      
        except Exception as e:
            logger.error(f"Error updating registers: {e}")
    
    async def update_loop(self):
        """Periodically update register values."""
        while not shutdown_event.is_set():
            self._update_registers()
            try:
                # Wait for the update interval or until shutdown is requested
                await asyncio.wait_for(
                    shutdown_event.wait(),
                    timeout=self.update_interval
                )
            except asyncio.TimeoutError:
                # This is expected after the timeout (update_interval)
                pass
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                break

async def run_server(host="0.0.0.0", port=5020):
    """Run the Modbus server."""
    simulator = InverterSimulator(update_interval=5)
    
    # Setup signal handlers
    def signal_handler():
        logger.info("Shutdown signal received, stopping server...")
        shutdown_event.set()  # Signal all tasks to stop
    
    # Register signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)
    
    # Start the update loop as a background task
    update_task = asyncio.create_task(simulator.update_loop())
    
    # Start the Modbus server
    logger.info(f"Starting Modbus server on {host}:{port}")
    
    try:
        # Create and start the server
        server = await StartAsyncTcpServer(
            context=simulator.datastore,
            address=(host, port)
        )
        
        # Wait until shutdown is requested
        await shutdown_event.wait()
    except OSError as e:
        if e.errno == 13:  # Permission denied
            logger.error(f"Permission denied when trying to use port {port}. Try using sudo or a port > 1024.")
        else:
            logger.error(f"Server error: {e}")
        shutdown_event.set()  # Signal to stop
    except Exception as e:
        logger.error(f"Server error: {e}")
        shutdown_event.set()  # Signal to stop
    finally:
        logger.info("Server shutdown initiated...")
        
        # Clean exit of update task
        if not update_task.done():
            # Wait briefly for task to respond to shutdown event
            try:
                await asyncio.wait_for(update_task, timeout=2.0)
            except asyncio.TimeoutError:
                logger.warning("Update task did not exit cleanly, forcing cancellation")
                update_task.cancel()
                try:
                    await update_task
                except asyncio.CancelledError:
                    pass
        
        logger.info("Server shutdown complete.")

def run_simulator(host="0.0.0.0", port=5020):
    """Run the simulator with a synchronous interface."""
    try:
        # Using a separate function ensures clean shutdown
        asyncio.run(run_server(host, port))
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.exception(f"Error running server: {e}")
    finally:
        # This ensures we always print this message when exiting
        logger.info("Simulator stopped.")
        
        # Force exit to avoid hanging
        sys.exit(0)

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = "0.0.0.0"
        
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    else:
        port = 5020  # Default to a non-privileged port
    
    # Run the simulator
    run_simulator(host, port)