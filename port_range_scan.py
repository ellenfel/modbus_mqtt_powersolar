from pymodbus.client import ModbusTcpClient

# Inverter IP address
INVERTER_IP = '192.168.1.100'

# Range of ports to test
START_PORT = 0
END_PORT = 2000

def test_modbus_connection(ip, port):
    """Attempt to connect to a Modbus server at the specified IP and port."""
    client = ModbusTcpClient(ip, port=port)
    connection = client.connect()
    client.close()
    return connection

def main():
    for port in range(START_PORT, END_PORT + 1):
        result = test_modbus_connection(INVERTER_IP, port)
        if result:
            print(f"Connection successful on port {port}")
        else:
            print(f"Connection failed on port {port}")

if __name__ == "__main__":
    main()

