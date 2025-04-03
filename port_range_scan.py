from pymodbus.client import ModbusTcpClient
import time

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
    successful_ports = []
    start_time = time.time()
    
    print(f"Starting port scan on {INVERTER_IP} from port {START_PORT} to {END_PORT}")
    print("-" * 50)

    for port in range(START_PORT, END_PORT + 1):
        result = test_modbus_connection(INVERTER_IP, port)
        if result:
            print(f"✓ Connection successful on port {port}")
            successful_ports.append(port)
        else:
            print(f"✗ Port {port}", end='\r')

    # Summary report
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"Scan completed in {elapsed_time:.2f} seconds")
    print(f"Tested port range: {START_PORT}-{END_PORT}")
    
    if successful_ports:
        print("\nSuccessful connections found on ports:")
        print("-" * 30)
        for port in successful_ports:
            print(f"Port {port}")
    else:
        print("\nNo successful connections found.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()