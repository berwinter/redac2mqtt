#!/usr/bin/env python3
import argparse
from src.mqtt import MqttClient
from src.cul import CulDevice
from src.database import Database
from src.homeassistant import DeviceDescriptions
from src.config import Config
from datetime import datetime
from contextlib import nullcontext
import logging
_LOGGER = logging.getLogger(__name__)


def main(config):
    with (CulDevice(config.device) as cul,
          MqttClient(config.broker, config.port, config.username, config.password, config.topic) if config.mqtt else nullcontext() as mqtt,
          Database(config.dbFile) if config.db else nullcontext() as db):
        if config.hass:
            hassDevices = DeviceDescriptions()
        _LOGGER.info("Write sqlite DB...")
        try:
            for telegram in cul.receiveMessages():
                if str(telegram.id) in config.meters and telegram.isNoLog():
                    if config.hass:
                        hassDevices.publishDiscovery(mqtt, telegram)     
                    if config.mqtt:
                        _LOGGER.debug(f"Sending {config.topic}/{telegram.id}/state")
                        mqtt.publish(telegram)
                if config.db:
                    db.commit(telegram)
                _LOGGER.debug(f"{datetime.fromtimestamp(telegram.timestamp)} | Len: {telegram.length} | {telegram.rssi:.1f} dBm | {telegram.lqi}")
        except KeyboardInterrupt:
            _LOGGER.info("Got CTRL+C")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read REDAC bus and publish messages via MQTT.')
    parser.add_argument('device', help="CUL device path (e.g. /dev/ttyACM0)")
    parser.add_argument('meter', help="File containig the IDs of the meters to track", type=open)
    parser.add_argument('--mqtt', help="Enable MQTT publish")
    parser.add_argument('--hass', help="Enable Homeassistant MQTT discovery messages")
    parser.add_argument('--database', help="Enable dumping of all messages into SQLite database")
    parser.add_argument('--debug', help="Enable debugging messgaes", action='store_true')

    main(Config(parser.parse_args()))
