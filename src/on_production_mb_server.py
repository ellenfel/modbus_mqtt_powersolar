from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

def run_modbus_server():
    # Insert a dummy register at index 0
    test_values = [
        0,      # Dummy register (will map to 40001 if using CLI with 1-based addressing)
        253,    # 40002 -> 25.3°C (253 * 0.1)
        23245,  # 40003 -> 232.45V (23245 * 0.01)
        0,      # 40004 (high word for 32-bit value)
        4127    # 40005 (low word for 32-bit value) -> 4.127kW (4127 * 0.001)
    ]
    
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, test_values)
    )
    context = ModbusServerContext(slaves=store, single=True)
    StartTcpServer(context, address=("0.0.0.0", 502))

if __name__ == "__main__":
    print("Starting Modbus TCP Server at 0.0.0.0:502")
    run_modbus_server()
