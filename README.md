Installation
============

This program utilizes node-red programming environment, mosquitto MQTT broker and python.

```
python3 -m venv venv
. venv/bin/activate
python3 -m pip install -r requirements.txt
```

Copy `config.dist.py` to `config.py` and fill out passwords and other local configuration.

Main files:
  - `lights.py` is ModbusTCP controller class;
  - `mqtt_bridge.py` MQTT client that serves lights class data to MQTT
  - `config.py` configuration

Mosquitto Configuration
=======================
Extra configuration is under [resources/lightcontroller.conf](resources/lightcontroller.conf).
Copy that file to `/etc/mosquitto/conf.d`.

Generate a password with:
```
mkdir /etc/mosquitto/passwords
chown mosquitto: /etc/mosquitto/passwords
chmod go= /etc/mosquitto/passwords
mosquitto_passwd -c /etc/mosquitto/passwords/passwords first_user
```
Add additional users with:
```
mosquitto_passwd -b /etc/mosquitto/passwords/passwords additional_user
```




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
