"""
Light control over Modbbus/TCP
"""
__author__ = "Kristaps Enkuzens"
__copyright__ = "Copyright (C) 2020 Kristaps Enkuzens"


import time
from pyModbusTCP.client import ModbusClient

clients = [
    ModbusClient(host='192.168.200.104', auto_open=True, auto_close=True),
    ModbusClient(host='192.168.200.129', auto_open=True, auto_close=True)
]

def status():
    for c in clients:
        # By default clients are auto close, but here we disable autoclose
        # as we will be reading watchdog timers etc.
        c.auto_close(False);
        print("Connecting to ", c.host())
        buscoupler_status = c.read_holding_registers(0x100c)[0]
        print("Buscoupler status: ", bin(buscoupler_status))
        if buscoupler_status & 1<<0: print("Bus terminal error") 
        if buscoupler_status & 1<<1: print("Bus coupler configuration error") 
        if buscoupler_status & 1<<15:
            print("Fieldbus error, watchdog timer elapsed") 
            print("Resetting watchdog")
            c.write_single_register(0x1121, 0xbecf)
            c.write_single_register(0x1121, 0xaffe)
        # Disable the watchdog
        watchdog_timeout = c.read_holding_registers(0x1120)[0]
        if (watchdog_timeout > 0):
            print("Watchdog timeout:", watchdog_timeout)
            print("Turning off");
            c.write_single_register(0x1120, 0)
        print("Number of outputs: ", c.read_holding_registers(0x1012))
        print("Number of inputs:  ", c.read_holding_registers(0x1013))
        print("Watchdog time: ", c.read_holding_registers(0x1020))
        c.auto_close(True);
        c.close()

def demo(c):
    c.open()
    c.write_single_coil(0,True)
    for i in range(1,12):
        print("X", end='', flush=True)
        time.sleep(0.1)
        c.write_single_coil(i-1,False)
        c.write_single_coil(i,True)
    print("X", end='', flush=True)
    c.write_single_coil(0,False)
    for i in range(0,12):
        print("O", end='', flush=True)
        time.sleep(0.1)
        c.write_single_coil(i,True)
    for i in range(0,12):
        print("N", end='', flush=True)
        time.sleep(0.1)
        c.write_single_coil(i,False)
    print("")
    c.close();

status()

