import os

import paho.mqtt.client as paho_mqtt

MQTT_URL = os.environ.get("MQTT_BROKER_URL")
MQTT_PORT = os.environ.get("MQTT_BROKER_PORT")

mqtt = None
app = None


def mqtt_init(flask_app):
    global mqtt
    global app

    app = flask_app
    mqtt = paho_mqtt.Client()

    mqtt.max_queued_messages_set(1000)
    mqtt.connect(MQTT_URL, int(MQTT_PORT))


def mqtt_publish_message(topic, payload):
    if mqtt is None:
        raise Exception("MQTT - mqtt client not initialized")

    mqtt.publish(topic, payload)
