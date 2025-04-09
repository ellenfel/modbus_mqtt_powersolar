#!/usr/bin/env python3
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import asyncio
import logging

# For pymodbus 3.x - import the async server
from pymodbus.server import StartAsyncTcpServer

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger()

async def run_server():
    # Solar inverter register values
    solar_values = [
        0,      # Dummy register at 0 (will map to 40001)
        0, 0, 0,  # Alarms (all clear)
        285,    # PV 1 voltage (28.5V) - multiply by 0.1
        450,    # PV 1 current (4.5A) - multiply by 0.01
        290,    # PV 2 voltage (29.0V) - multiply by 0.1
        430,    # PV 2 current (4.3A) - multiply by 0.01
        2500,   # Input power (2.5kW) - multiply by 0.001
        3200,   # Peak power (3.2kW) - multiply by 0.001
        2300,   # Active power (2.3kW) - multiply by 0.001
        8500    # Daily energy yield (8.5kWh) - multiply by 0.001
    ]
    
    # Create data store
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, solar_values)
    )
    
    context = ModbusServerContext(slaves=store, single=True)
    
    # Start server
    logger.info("Starting Modbus TCP Server on port 502")
    await StartAsyncTcpServer(
        context=context,
        address=("0.0.0.0", 502)
    )

if __name__ == "__main__":
    # Run the async server
    asyncio.run(run_server())