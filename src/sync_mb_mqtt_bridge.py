#!/usr/bin/env python3
"""Modbus TCP client for inverter connection"""

import pymodbus.client as ModbusClient
from pymodbus import pymodbus_apply_logging_config

def run_inverter_client():
    """Connect to inverter and read data."""
    # Setup logging
    pymodbus_apply_logging_config("DEBUG")
    
    # Connection parameters
    host = "192.168.1.100"
    port = 502
    
    print(f"Connecting to inverter at {host}:{port}")
    client = ModbusClient.ModbusTcpClient(
        host,
        port=port,
        timeout=10,
        retries=3,
    )
    
    # Set the slave ID before connecting
    client.slave = 1
    
    print("Establishing connection...")
    connection = client.connect()
    if not connection:
        print("Failed to connect to the inverter")
        return
    
    print("Successfully connected")
    
    try:
        # Read temperature value (register 1 = 40002)
        print("Reading temperature data...")
        temp_response = client.read_holding_registers(1, 1)
        if hasattr(temp_response, 'isError') and temp_response.isError():
            print(f"Error reading temperature: {temp_response}")
        else:
            temperature = temp_response.registers[0] * 0.1
            print(f"Temperature: {temperature}°C")
        
        # Read voltage value (register 2 = 40003)
        print("Reading voltage data...")
        voltage_response = client.read_holding_registers(2, 1)
        if hasattr(voltage_response, 'isError') and voltage_response.isError():
            print(f"Error reading voltage: {voltage_response}")
        else:
            voltage = voltage_response.registers[0] * 0.01
            print(f"Voltage: {voltage}V")
        
        # Read power value (registers 3-4 = 40004-40005)
        print("Reading power data...")
        power_response = client.read_holding_registers(3, 2)
        if hasattr(power_response, 'isError') and power_response.isError():
            print(f"Error reading power: {power_response}")
        else:
            # Manually convert to 32-bit value
            high_word = power_response.registers[0]
            low_word = power_response.registers[1]
            power_value = (high_word << 16) | low_word
            power = power_value * 0.001
            print(f"Power: {power}kW")
            
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        import traceback
        traceback.print_exc()
    finally:
        print("Closing connection")
        client.close()

if __name__ == "__main__":
    run_inverter_client()