#!/usr/bin/env python3
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusTcpServer
from twisted.internet import reactor
import logging

logging.basicConfig(level=logging.INFO)

def run_modbus_server():
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * 100),
        co=ModbusSequentialDataBlock(0, [0] * 100),
        hr=ModbusSequentialDataBlock(40001, [253, 23245, 4127, 0, 0]), # initial values for registers
        ir=ModbusSequentialDataBlock(0, [0] * 100)
    )

    context = ModbusServerContext(slaves=store, single=True)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = '1.0'

    StartTcpServer(context, identity=identity, address=("0.0.0.0", 502)) # Listen on all interfaces.
    reactor.run()

if __name__ == "__main__":
    run_modbus_server()