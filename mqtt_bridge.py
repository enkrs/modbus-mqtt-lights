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

NAME = config.mqtt_controller_name

controllers = {}
light_state = {}


def on_message(client, userdata, msg):
    logger.debug(msg.topic+" "+str(msg.payload))

logger.debug("Connecting to mqtt server")
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.username_pw_set(config.mqtt_user, config.mqtt_pass)
mqttc.connect(config.mqtt_host, config.mqtt_port)
mqttc.loop_start()

def initialize():
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
        # Read current output state and publish it
        light_state[group] = controllers[group].outputs()
        # TODO: THE ABOVE LINE SHOULD READ INPUTS!!!
        for idx in range(controllers[group].num_outputs):
            mqttc.publish(f"homie/{NAME}/{group}/{idx}/$name", f"Light {idx}", retain=True)
            mqttc.publish(f"homie/{NAME}/{group}/{idx}/$type", "Standarta apgaismojums", retain=True)
            mqttc.publish(f"homie/{NAME}/{group}/{idx}/$properties", "power", retain=True)
            mqttc.publish(f"homie/{NAME}/{group}/{idx}/power/$name", "Lampa", retain=True)
            mqttc.publish(f"homie/{NAME}/{group}/{idx}/power/$datatype", "boolean", retain=True)
            mqttc.publish(f"homie/{NAME}/{group}/{idx}/power/$settable", "true", retain=True)
            mqttc.publish(f"homie/{NAME}/{group}/{idx}/power", light_state[group][idx], retain=True)
        logger.debug("Subscribing to %s", f"homie/{NAME}/{group}/+/power/set")
        mqttc.subscribe(f"homie/{NAME}/{group}/+/power/set")
        mqttc.subscribe(f"#")

    logger.debug("Ready")
    mqttc.publish(f"homie/{NAME}/$state", "ready", retain=True)


def run():
    try:
        while True:
            for group, controller in controllers.items():
                controller.check_status()
                controller.inputs()
                # TODO: this should monitor inputs
                current_outputs = controller.outputs()
                for idx, val in enumerate(current_outputs):
                    if light_state[group][idx] != val:
                        logger.debug("Light %d changed to %s", idx, str(val))
                        mqttc.publish(f"homie/{NAME}/{group}/{idx}/power", "true" if val else "false")
                        light_state[group][idx] = val
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info('Exitting')
        mqttc.publish(f"homie/{NAME}/$state", "disconnected", retain=True)
        mqttc.loop_stop()

initialize()
run()
