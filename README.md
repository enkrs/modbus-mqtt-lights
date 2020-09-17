Installation
============

```
python3 -m venv venv
. venv/bin/activate
python3 -m pip install -r requirements.txt
```

Main files:
  - `lights.py` is ModbusTCP controller class;
  - `mqtt_bridge.py` MQTT client that serves lights class data to MQTT
  - `config.py` configuration

Examples
========

```
from pyModbusTCP.client import ModbusClient
c1 = ModbusClient(host='192.168.200.104',auto_open=True,auto_close=True);
c2 = ModbusClient(host='192.168.200.129',auto_open=True,auto_close=True);
```

```
c.open() # Reset watchdog:
c.write_single_register(0x1121,0xbecf)
c.write_single_register(0x1121,0xaffe)
c.close()
```

```
print("Watchdog time: ", c.read_holding_registers(0x1020))
```

```
c.read_holding_registers(0x1012) # Number of digital outputs
c.read_holding_registers(0x1013) # Number of digital inputs
```
