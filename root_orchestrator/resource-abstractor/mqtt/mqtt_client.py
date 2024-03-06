import os

from paho.mqtt import client as mqtt_client

MQTT_URL = os.environ.get("MQTT_BROKER_URL")
MQTT_PORT = os.environ.get("MQTT_BROKER_PORT")
HOOKS_TOPIC = "root/hooks"


class MqttClient:
    def __init__(self):
        self.mqtt = mqtt_client.Client()

    def connect(self, blocking=False):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Connected to mqtt broker with result code {rc}")
            else:
                print(f"Failed to connect to mqtt broker with result code {rc}")

        self.mqtt.on_connect = on_connect
        self.mqtt.connect(MQTT_URL, int(MQTT_PORT))
        if blocking:
            self.mqtt.loop_forever()
        else:
            self.mqtt.loop_start()

    def publish_message(self, topic, payload):
        return self.mqtt.publish(topic, payload)

    def subcribe_to(self, topic):
        # TODO: check response of subscribing
        self.mqtt.subscribe(topic)

        def on_message(client, userdata, message):
            print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

        self.mqtt.on_message = on_message

    def stop(self):
        self.mqtt.loop_stop()
