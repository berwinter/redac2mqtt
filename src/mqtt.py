from paho.mqtt import client as mqtt_client
import json
import random
import logging
_LOGGER = logging.getLogger(__name__)


class MqttClient:
    def __init__(self, broker, port, username, password, topic):
          self._client_id = f'redac2mqtt-{random.randint(0, 1000)}'
          self._broker = broker
          self._port = port
          self._username = username
          self._password = password
          self._topic = topic

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            _LOGGER.info("Connected to MQTT Broker!")
        else:
            _LOGGER.error("Failed to connect, return code %d\n", rc)

    def __enter__(self):
        self._client = mqtt_client.Client(self._client_id)
        self._client.username_pw_set(self._username, self._password)
        self._client.on_connect = self._on_connect
        self._client.connect(self._broker, self._port)
        self._client.loop_start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.loop_stop()

    def publishDiscovery(self, sensor):
        self._publish(f"homeassistant/sensor/{sensor['unique_id']}/config", json.dumps(sensor))

    def publishTelegram(self, telegram):
        self._publish(f"{self._topic}/{telegram.id}/state", json.dumps(telegram.getData(), indent = 4))

    def _publish(self, topic, message):
            result = self._client.publish(topic, message, retain=True)
            status = result[0]
            if status != 0:
                _LOGGER.warning(f"Failed to send message to topic {topic}")
