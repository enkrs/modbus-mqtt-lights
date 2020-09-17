"""
Light control over Modbbus/TCP

Connects to Modbus module and provides functions to
read inputs/outputs and toggle outputs.
"""
__author__ = "Kristaps Enkuzens"
__copyright__ = "Copyright (C) 2020 Kristaps Enkuzens"

import time
import logging
from pyModbusTCP.client import ModbusClient
import config

logger = logging.getLogger(__name__)

class LightController():
    """Class to control lights of a single controller"""

    toggle_time = config.toggle_time

    def __init__(self, host):
        self.client = ModbusClient(host=host, auto_open=True, auto_close=False)
        #self.client.debug(True)
        logger.info("Connecting to %s", self.client.host())

        status = self.check_status()
        if status & 1<<15:
            # Watchdog ellapsed, try to reset
            logger.info("Resetting watchdog")
            self.client.write_single_register(0x1121, 0xbecf)
            self.client.write_single_register(0x1121, 0xaffe)

        # Disable the watchdog, if enabled
        watchdog_timeout = self.client.read_holding_registers(0x1120)[0]
        if watchdog_timeout > 0:
            logger.debug("Watchdog timeout: %d", watchdog_timeout)
            logger.info("Disabling watchdog")
            self.client.write_single_register(0x1120, 0)

        (self.num_outputs, self.num_inputs) = self.client.read_holding_registers(0x1012, 2)
        logger.info("Number of outputs: %d", self.num_outputs)
        logger.info("Number of inputs: %d", self.num_inputs)
        self.client.close()
        # We use auto close for all subsequent calls after initialization
        self.client.auto_close(True)

    def check_status(self):
        """Read buscoupler status from the module"""
        buscoupler_status = self.client.read_holding_registers(0x100c)[0]
        if buscoupler_status & 1<<0:
            logger.error("Bus terminal error")
        if buscoupler_status & 1<<1:
            logger.error("Bus coupler configuration error")
        if buscoupler_status & 1<<15:
            logger.error("Fieldbus error, watchdog timer elapsed")
        return buscoupler_status

    def inputs(self):
        """Read input status from module"""
        inputs = self.client.read_discrete_inputs(0, self.num_inputs)
        logger.debug("Inputs: %s", "".join(map(lambda c: '1' if c else '0', inputs)))
        return inputs

    def outputs(self):
        """Read output status from module"""
        coils = self.client.read_coils(0, self.num_outputs)
        logger.debug("Outputs: %s", "".join(map(lambda c: '1' if c else '0', coils)))
        return coils

    def toggle(self, bit_addr):
        """Toggle a impulse relay connected to a single output"""
        logger.info("Toggling %d on %s", bit_addr, self.client.host())
        self.client.auto_close(False)
        self.client.write_single_coil(bit_addr, True)
        logger.debug("On %d", bit_addr)
        time.sleep(self.toggle_time)
        self.client.write_single_coil(bit_addr, False)
        logger.debug("Off %d", bit_addr)
        self.client.close()
        self.client.auto_close(True)
