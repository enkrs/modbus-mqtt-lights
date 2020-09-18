"""
MQTT bridge

Presents LightController status via MQTT messages
"""
__author__ = "Kristaps Enkuzens"
__copyright__ = "Copyright (C) 2020 Kristaps Enkuzens"

import time
from Threading import Thread
from Queue import Queue
import logging
import sys
import re
import paho.mqtt.client as mqtt
import config
from lights import LightController

logging.basicConfig(
    stream=sys.stderr,
    format=config.log_format,
    level=getattr(logging, config.log_level)
)

logger = logging.getLogger(__name__)

NAME = config.mqtt_controller_name

controllers = {}
light_state = {}
_dummy_inputs = {} # this will emulate inputs while not connected

mqttc = mqtt.Client()

def mqtt_bool(payload):
    """Helper function to convert mqtt received payload to boolean"""
    return payload.lower().decode() in ['true', 'on', '1']

def set_light(node, idx, power):
    """ Set the light to required state """
    logger.info("Setting light %s/%d %s", node, idx, "On" if power else "Off")
    if light_state[node][idx] != power:
        mqttc.publish(f"homie/{NAME}/{group}-{idx}/power", "true" if state else "false")
        controllers[node].toggle(idx)
        _dummy_inputs[node][idx] = power #TODO, this will come from hardware to inputs

def on_message(client, userdata, msg):
    """Handle all subscribed MQTT topics"""
    logger.debug("MQTT Message received: %s", msg.topic+" "+str(msg.payload))

    regex = r"homie\/([a-z0-9-]*)\/([a-z0-9-]*)-([0-9]*)\/power\/set"
    matches = re.search(regex, msg.topic)
    if matches and matches.group(1) == NAME:
        logger.debug("name %s, node %s, light %s", matches.group(1), matches.group(2), matches.group(3))
        node = matches.group(2)
        idx = matches.group(3)
        state = mqtt_bool(msg.payload)
        set_light(node, int(idx), state)

def on_connect(client, userdata, flags, rc):
    """Handle mqtt connection status"""
    logger.info("Connected with result code "+str(rc))
    if rc == mqtt.MQTT_ERR_SUCCESS:
        # Reinitialize on establishing and re-establishing connection
        initialize()

def handle_queue(q):
    while not q.empty():
        print(q.get())
        q.task_done()

def check_light_changes(group):
    """Check for changes in Modbus/TCP status and publish to MQTT"""
    logger.debug("Controller %s", group)
    controllers[group].inputs()
    controllers[group].outputs()
    logger.debug("Dummys: %s", "".join(map(lambda c: '1' if c else '0', _dummy_inputs[group])))
    # TODO: this should monitor inputs
    for idx, val in enumerate(_dummy_inputs[group]):
        if light_state[group][idx] != val:
            logger.debug("Light %d changed to %s", idx, str(val))
            mqttc.publish(f"homie/{NAME}/{group}-{idx}/power", "true" if val else "false")
            light_state[group][idx] = val

def initialize():
    """Read data from Modbus/TCP and publish it to MQTT"""
    logger.info("Initializing controllers")
    for group, host in config.controllers.items():
        controllers[group] = LightController(host)

    logger.info("Publishing bridge data to mqtt")
    mqttc.publish(f"homie/{NAME}/$homie", "4.0.0", retain=True)
    mqttc.publish(f"homie/{NAME}/$name", "Light control panel", retain=True)
    mqttc.publish(f"homie/{NAME}/$state", "init", retain=True)
    mqttc.publish(f"homie/{NAME}/$extensions", "", retain=True)
    mqttc.will_set(f"homie/{NAME}/$state", payload="lost", qos=0, retain=True)
    # Creates string "office-1,office-2,warehouse-1,warehouse-2,warehouse3"
    nodes = ",".join(
        ",".join( f"{group}-{str(i)}" for i in range(controllers[group].num_outputs)
    ) for group in controllers)
    mqttc.publish(f"homie/{NAME}/$nodes", nodes, retain=True)

    for group, host in config.controllers.items():
        controllers[group] = LightController(host)
        logger.info("Publishing controller \"%s\" data to mqtt", group)
        # Read current output state and publish it
        light_state[group] = controllers[group].outputs() # TODO Use inputs
        _dummy_inputs[group] = controllers[group].outputs() ## TODO Delete this line when using inputs
        for idx in range(controllers[group].num_outputs):
            mqttc.publish(f"homie/{NAME}/{group}-{idx}/$name", f"Light {idx}", retain=True)
            mqttc.publish(f"homie/{NAME}/{group}-{idx}/$type", "Standarta apgaismojums", retain=True)
            mqttc.publish(f"homie/{NAME}/{group}-{idx}/$properties", "power", retain=True)
            mqttc.publish(f"homie/{NAME}/{group}-{idx}/power/$name", "Lampa", retain=True)
            mqttc.publish(f"homie/{NAME}/{group}-{idx}/power/$datatype", "boolean", retain=True)
            mqttc.publish(f"homie/{NAME}/{group}-{idx}/power/$settable", "true", retain=True)
            mqttc.publish(f"homie/{NAME}/{group}-{idx}/power", "true" if light_state[group][idx] else "false", retain=True)
    mqttc.subscribe(f"homie/{NAME}/+/power/set")
    mqttc.publish(f"homie/{NAME}/$state", "ready", retain=True)

def run():
    mqttc.loop_start()
    try:
        while True:
            # Refresh controller changes periodically
            for group, controller in controllers.items():
                controller.check_status()
                check_light_changes(group)
            time.sleep(3)
    except (KeyboardInterrupt, SystemExit):
        logger.info('Exitting')
        msg = mqttc.publish(f"homie/{NAME}/$state", "disconnected", retain=True)
        msg.wait_for_publish()
        mqttc.disconnect()


logger.debug("Connecting to mqtt server")
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(config.mqtt_user, config.mqtt_pass)
mqttc.connect(config.mqtt_host, config.mqtt_port)
run()
mqttc.loop_stop()
