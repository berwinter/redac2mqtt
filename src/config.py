import urllib
import logging
_LOGGER = logging.getLogger(__name__)


class Config:
    def __init__(self, args):
        self.device = args.device
        self.hass = args.hass
        self.mqtt = False
        self.username = ""
        self.password = ""
        self.broker = ""
        self.port = ""
        self.topic = "redac"
        self.db = False
        self.dbFile = ""
        self.meters = [int(x.strip()) for x in args.meter.readlines()]

        if args.mqtt:
            self.mqtt = True
            mqtt = urllib.parse.urlparse(args.mqtt)
            self.username = mqtt.username
            self.password = mqtt.password
            self.broker = mqtt.hostname
            self.port = mqtt.port
            
        if args.database:
            self.db = True
            self.dbFile = args.database

        if args.debug:
            logging.basicConfig(level=logging.DEBUG)
        


