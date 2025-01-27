from src.redac import HeatMeter, WarmWaterMeter, ColdWaterMeter
import logging
_LOGGER = logging.getLogger(__name__)


class DeviceDescriptions:
    def __init__(self):
        self._publishedIds = set()
        self._meters = {
            HeatMeter: HeatingMeterDescription("ELF"),
            ColdWaterMeter: ColdWaterMeterDescription("WMRA2-OPT"),
            WarmWaterMeter: WarmWaterMeterDescription("WMRA1-C")
        }

    def publishDiscovery(self, mqtt, telegram):
        if telegram.id not in self._publishedIds:
            for sensor in self._meters[type(telegram)].getDescription(telegram.id):
                mqtt.publishDiscovery(sensor)
            self._publishedIds.add(telegram.id)

class MeterDescription:
    sensors = None
    def __init__(self, model):
        self.model = model

    def getDescription(self, id):
        first = True
        for s in self.sensors:
            data = {
                "device_class": s.type,
                "state_class": 'total',
                "state_topic": f"redac/{id}/state",
                "unit_of_measurement": s.unit,
                "value_template": "{{ " + f"value_json.{s.name}" + " }}",
                "unique_id":f"redac_{id}_{s.name}",
                "device":{
                    "identifiers":[
                        f"redac_{id}"
                    ]
                }
            }
            if first:
                data["device"]["name"] = f"{self.name} ({id})"
                data["device"]["manufacturer"] = "Messtechnik GmbH"
                data["device"]["model"] = self.model
                data["device"]["serial_number"] = id
                first = False
            yield data

class SensorDescription:
    def __init__(self, name, type, unit):
        self.name = name
        self.type = type
        self.unit = unit

class HeatingMeterDescription(MeterDescription):
    name = 'Heating'
    sensors = [SensorDescription('totalEnergy', 'energy', 'kWh'), SensorDescription('totalFlow', 'volume', 'm³')]

class WaterMeterDescription(MeterDescription):
    sensors = [SensorDescription('currentValue', 'water', 'm³')]

class ColdWaterMeterDescription(WaterMeterDescription):
    name = "Coldwater"

class WarmWaterMeterDescription(WaterMeterDescription):
    name = "Warmwater"
