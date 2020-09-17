"""
MQTT bridge

Presents LightController status via MQTT messages
"""
__author__ = "Kristaps Enkuzens"
__copyright__ = "Copyright (C) 2020 Kristaps Enkuzens"

import time
import logging
import sys
import paho.mqtt.client as mqtt
import config
from lights import LightController

logger = logging.getLogger(__name__)

logging.basicConfig(
    stream=sys.stderr,
    format=config.log_format,
    level=getattr(logging, config.log_level)
)

mqttc = mqtt.Client()
logger.debug("Connecting to mqtt server")
mqttc.username_pw_set(config.mqtt_user, config.mqtt_pass)
mqttc.connect(config.mqtt_host, config.mqtt_port)
mqttc.loop_start()

NAME = config.mqtt_controller_name

controllers = {}
logger.info("Publishing bridge data to mqtt")
mqttc.publish(f"homie/{NAME}/$homie", "4.0.0", retain=True)
mqttc.publish(f"homie/{NAME}/$name", "Light control panel", retain=True)
mqttc.publish(f"homie/{NAME}/$state", "init", retain=True)
mqttc.publish(f"homie/{NAME}/$extensions", "", retain=True)
mqttc.will_set(f"homie/{NAME}/$state", payload="lost", qos=0, retain=True)
mqttc.publish(
    f"homie/{NAME}/$nodes",
    ','.join(f"{key}[]" for key in config.controllers),
    retain=True)

for group, host in config.controllers.items():
    controllers[group] = LightController(host)
    logger.info("Publishing controller \"%s\" data to mqtt", group)
    for i in range(controllers[group].num_outputs):
        mqttc.publish(f"homie/{NAME}/{group}/{i}/$name", f"Light {i}", retain=True)
        mqttc.publish(f"homie/{NAME}/{group}/{i}/$type", "Standarta apgaismojums", retain=True)
        mqttc.publish(f"homie/{NAME}/{group}/{i}/$properties", "power", retain=True)
        mqttc.publish(f"homie/{NAME}/{group}/{i}/power/$name", "Lampa", retain=True)
        mqttc.publish(f"homie/{NAME}/{group}/{i}/power/$datatype", "boolean", retain=True)
        mqttc.publish(f"homie/{NAME}/{group}/{i}/power/$settable", "true", retain=True)

logger.debug("Ready")
mqttc.publish(f"homie/{NAME}/$state", "ready", retain=True)

try:
    while True:
        for topic, controller in controllers.items():
            controller.check_status()
            controller.inputs()
            controller.outputs()
        time.sleep(2)
except (KeyboardInterrupt, SystemExit):
  logger.info('Exitting')
  mqttc.publish(f"homie/{NAME}/$state", "disconnected", retain=True)

