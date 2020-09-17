"""
Test script for lights module
"""
__author__ = "Kristaps Enkuzens"
__copyright__ = "Copyright (C) 2020 Kristaps Enkuzens"

import logging
import sys
import config
from lights import LightController

logging.basicConfig(
    stream=sys.stderr,
    format=config.log_format,
    level=getattr(logging, config.log_level)
)

logger = logging.getLogger(__name__)

logger.debug("Starting tests")
for host in config.controllers:
    logger.debug("Testing %s", host)
    c = LightController(host)
    c.inputs()
    c.outputs()
    c.check_status()
    c.toggle(1)
    c.check_status()
    c.toggle(2)
    c.check_status()
