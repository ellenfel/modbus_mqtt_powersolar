from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

def run_modbus_server():
    # Initialize test data for holding registers
    # Structure: [Temperature, Voltage, Power_High, Power_Low]
    test_values = [
        253,    # 40001 -> 25.3°C (253 * 0.1)
        23245,  # 40002 -> 232.45V (23245 * 0.01)
        0,      # 40003 (high word for 32-bit value)
        4127    # 40004 (low word for 32-bit value) -> 4.127kW (4127 * 0.001)
    ]
    
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, test_values)
    )
    context = ModbusServerContext(slaves=store, single=True)
    StartTcpServer(context, address=("0.0.0.0", 502))

if __name__ == "__main__":
    print("Starting Modbus TCP Server at 0.0.0.0:502")
    run_modbus_server()