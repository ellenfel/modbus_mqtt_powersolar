Examples
========

Examples are divided in 2 parts:

The first part are some simple client examples which can be copied and run directly.
These examples show the basic functionality of the library.

The second part are more advanced examples, but in order to not duplicate code,
this requires you to download the examples directory and run
the examples in the directory.

Ready to run examples:
----------------------

These examples are very basic examples,
showing how a client can communicate with a server.

You need to modify the code to adapt it to your situation.

Simple asynchronous client
^^^^^^^^^^^^^^^^^^^^^^^^^^
Source: :github:`examples/simple_async_client.py`

```
#!/usr/bin/env python3
"""Pymodbus asynchronous client example.

An example of a single threaded synchronous client.

usage: simple_async_client.py

All options must be adapted in the code
The corresponding server must be started before e.g. as:
    python3 server_sync.py
"""
import asyncio

import pymodbus.client as ModbusClient
from pymodbus import (
    FramerType,
    ModbusException,
    pymodbus_apply_logging_config,
)


async def run_async_simple_client(comm, host, port, framer=FramerType.SOCKET):
    """Run async client."""
    # activate debugging
    pymodbus_apply_logging_config("DEBUG")

    print("get client")
    client: ModbusClient.ModbusBaseClient
    if comm == "tcp":
        client = ModbusClient.AsyncModbusTcpClient(
            host,
            port=port,
            framer=framer,
            # timeout=10,
            # retries=3,
            # source_address=("localhost", 0),
        )
    elif comm == "udp":
        client = ModbusClient.AsyncModbusUdpClient(
            host,
            port=port,
            framer=framer,
            # timeout=10,
            # retries=3,
            # source_address=None,
        )
    elif comm == "serial":
        client = ModbusClient.AsyncModbusSerialClient(
            port,
            framer=framer,
            # timeout=10,
            # retries=3,
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            # handle_local_echo=False,
        )
    else:
        print(f"Unknown client {comm} selected")
        return

    print("connect to server")
    await client.connect()
    # test client is connected
    assert client.connected

    print("get and verify data")
    try:
        # See all calls in client_calls.py
        rr = await client.read_coils(1, count=1, device_id=1)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
        return
    if rr.isError():
        print(f"Received exception from device ({rr})")
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        client.close()
        return
    try:
        # See all calls in client_calls.py
        rr = await client.read_holding_registers(10, count=2, device_id=1)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
        return
    if rr.isError():
        print(f"Received exception from device ({rr})")
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        client.close()
        return
    value_int32 = client.convert_from_registers(rr.registers, data_type=client.DATATYPE.INT32)
    print(f"Got int32: {value_int32}")
    print("close connection")
    client.close()


if __name__ == "__main__":
    asyncio.run(
        run_async_simple_client("tcp", "127.0.0.1", 5020), debug=True
    )
```

Simple synchronous client
^^^^^^^^^^^^^^^^^^^^^^^^^^
Source: :github:`examples/simple_sync_client.py`

.. literalinclude:: ../../examples/simple_sync_client.py


Client performance sync vs async
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Source: :github:`examples/client_performance.py`

.. literalinclude:: ../../examples/client_performance.py


Advanced examples
-----------------

These examples are considered essential usage examples, and are guaranteed to work,
because they are tested automatilly with each dev branch commit using CI.

.. tip:: The examples needs to be run from within the examples directory, unless you modify them.
    Most examples use helper.py and client_*.py or server_*.py. This is done to avoid maintaining the
    same code in multiple files.

    - :download:`examples.zip <_static/examples.zip>`
    - :download:`examples.tgz <_static/examples.tgz>`


Client asynchronous calls
^^^^^^^^^^^^^^^^^^^^^^^^^
Source: :github:`examples/client_async_calls.py`

.. automodule:: examples.client_async_calls
    :undoc-members:
    :noindex:


Client asynchronous
^^^^^^^^^^^^^^^^^^^
Source: :github:`examples/client_async.py`

.. automodule:: examples.client_async
    :undoc-members:
    :noindex:


Client calls
^^^^^^^^^^^^
Source: :github:`examples/client_calls.py`

.. automodule:: examples.client_calls
    :undoc-members:
    :noindex:


Custom message
^^^^^^^^^^^^^^
Source: :github:`examples/custom_msg.py`

.. automodule:: examples.custom_msg
    :undoc-members:
    :noindex:


Client synchronous
^^^^^^^^^^^^^^^^^^
Source: :github:`examples/client_sync.py`

.. automodule:: examples.client_sync
    :undoc-members:
    :noindex:


Server asynchronous
^^^^^^^^^^^^^^^^^^^
Source: :github:`examples/server_async.py`

.. automodule:: examples.server_async
    :undoc-members:
    :noindex:


Server callback
^^^^^^^^^^^^^^^
Source: :github:`examples/server_callback.py`

.. automodule:: examples.server_callback
    :undoc-members:
    :noindex:


Server tracer
^^^^^^^^^^^^^
Source: :github:`examples/server_hook.py`

.. automodule:: examples.server_hook
    :undoc-members:
    :noindex:


Server synchronous
^^^^^^^^^^^^^^^^^^
Source: :github:`examples/server_sync.py`

.. automodule:: examples.server_sync
    :undoc-members:
    :noindex:


Server updating
^^^^^^^^^^^^^^^
Source: :github:`examples/server_updating.py`

.. automodule:: examples.server_updating
    :undoc-members:
    :noindex:


Simulator example
^^^^^^^^^^^^^^^^^
Source: :github:`examples/simulator.py`

.. automodule:: examples.simulator
    :undoc-members:
    :noindex:


Simulator datastore (shared storage) example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Source: :github:`examples/datastore_simulator_share.py`

.. automodule:: examples.datastore_simulator_share
    :undoc-members:
    :noindex:


Message Parser
^^^^^^^^^^^^^^
Source: :github:`examples/message_parser.py`

.. automodule:: examples.message_parser
    :undoc-members:
    :noindex:


Modbus forwarder
^^^^^^^^^^^^^^^^
Source: :github:`examples/modbus_forwarder.py`

.. automodule:: examples.modbus_forwarder
    :undoc-members:
    :noindex:


Examples contributions
----------------------

These examples are supplied by users of pymodbus.
The pymodbus team thanks for sharing the examples.

Solar
^^^^^
Source: :github:`examples/contrib/solar.py`

.. automodule:: examples.contrib.solar
    :undoc-members:
    :noindex:


Serial Forwarder
^^^^^^^^^^^^^^^^
Source: :github:`examples/contrib/serial_forwarder.py`

.. automodule:: examples.contrib.serial_forwarder
    :undoc-members:
    :noindex: