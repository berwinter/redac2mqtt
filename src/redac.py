import time
import struct
from datetime import datetime

class Telegram:
    RSSI_OFFSET = 74
    def TelegramFactory(data, timestamp=None):
        if data[3] & 0xf0 == 0x00:
            return HeatMeter(data, timestamp)
        elif data[3] & 0xf0 == 0x40:
            return ColdWaterMeter(data, timestamp)
        elif data[3] & 0xf0 == 0x50:
            return WarmWaterMeter(data, timestamp)
        else:
            return Telegram(data, timestamp)
        
    def __init__(self, data, timestamp=None):
        if timestamp:
            self.timestamp = timestamp
        else:
            self.timestamp = time.time()
        self.data = data
        (self.length, self.frameCounter, self.control, self.type, self.id, year, month, day, hour, minute, second) = struct.unpack("<BBBBL6B", self.data[0:14])
        self.metertime = datetime.timestamp(datetime.strptime(f"20{year}-{month}-{day} {hour}:{minute}:{second}", "%Y-%m-%d %H:%M:%S"))
        self.getLinkQuality()
        self.getSignalStrength()

    def getLinkQuality(self):
        self.lqi = (self.data[-2] ^ 0x80)
        return self.lqi
    
    def getSignalStrength(self):
        if self.data[-1] >= 128:
            self.rssi = float(self.data[-1]-256)/2.0 - self.RSSI_OFFSET
        else:
            self.rssi = float(self.data[-1])/2.0 - self.RSSI_OFFSET
        return self.rssi

    def _header(self):
        return f"{datetime.fromtimestamp(self.timestamp)}: {self.length:>4d} | {self.frameCounter:>3d} | {self.id:>10d} | {datetime.fromtimestamp(self.metertime)}"
    
    def _footer(self):
        return f"{self.rssi:.1f}dBm | {self.lqi}"
    
    def _rest(self, start):
        rest = ""
        for d in self.data[start:-2]:
            rest += f"{d:02X} "
        return rest
    
    def __str__(self):
        return f"{self._header()} | {self._rest(14)}| {self._footer()}"
    
    def isNoLog(self):
        return (self.length != 42 and self.length != 56)
    
    def getData(self):
        data = {'timestamp': str(datetime.fromtimestamp(self.timestamp)), 'metertime': str(datetime.fromtimestamp(self.metertime)), 'frameCounter': self.frameCounter, 'id': self.id, 'rssi': self.rssi, 'lqi': self.lqi}
        return data

class HeatMeter(Telegram):
    def __init__(self, data, timestamp=time.time()):
        super().__init__(data, timestamp)
        (currentMonthEnergy, currentMonthFlow, lastMonthEnergy, lastMonthFlow, lastLastMonthEnergy, lastLastMonthFlow, lastYearTotalEnergy, lastYearTotalFlow, lastLastYearTotalEnergy, lastLastYearTotalFlow) = struct.unpack("<6H4L", self.data[14:42])
        self.currentMonthEnergy = currentMonthEnergy/10
        self.currentMonthFlow = currentMonthFlow/10
        self.lastMonthEnergy = lastMonthEnergy/10
        self.lastMonthFlow = lastMonthFlow/10
        self.lastLastMonthEnergy = lastLastMonthEnergy/10
        self.lastLastMonthFlow = lastLastMonthFlow/10
        self.lastYearTotalEnergy = lastYearTotalEnergy/10
        self.lastYearTotalFlow = lastYearTotalFlow/10
        self.lastLastYearTotalEnergy = lastLastYearTotalEnergy/10
        self.lastLastYearTotalFlow = lastLastYearTotalFlow/10
    
    def __str__(self):
        return f"{self._header()} | {self.currentMonthEnergy:>10.1f} | {self.currentMonthFlow:>10.1f} | {self.lastMonthEnergy:>10.1f} | {self.lastMonthFlow:>10.1f} | {self.lastLastMonthEnergy:>10.1f} | {self.lastLastMonthFlow:>10.1f} | {self.lastYearTotalEnergy:>10.1f} | {self.lastYearTotalFlow:>10.1f} | {self.lastLastYearTotalEnergy:>10.1f} | {self.lastLastYearTotalFlow:>10.1f} |{self._rest(42)}| {self._footer()}"
    
    def getData(self):
        data = super().getData()
        data['currentMonthEnergy'] = self.currentMonthEnergy
        data['currentMonthFlow'] = self.currentMonthFlow
        data['lastMonthEnergy'] = self.lastMonthEnergy
        data['lastMonthFlow'] = self.lastMonthFlow
        data['lastLastMonthEnergy'] = self.lastLastMonthEnergy
        data['lastLastMonthFlow'] = self.lastLastMonthFlow
        data['lastYearTotalEnergy'] = self.lastYearTotalEnergy
        data['lastYearTotalFlow'] = self.lastYearTotalFlow
        data['lastLastYearTotalEnergy'] = self.lastLastYearTotalEnergy
        data['lastLastYearTotalFlow'] = self.lastLastYearTotalFlow
        data['totalEnergy'] = self.lastYearTotalEnergy + self.currentMonthEnergy
        data['totalFlow'] = self.lastYearTotalFlow + self.currentMonthFlow
        return data

class WaterMeter(Telegram):
    def __init__(self, data, timestamp=time.time()):
        super().__init__(data, timestamp)
        (currentValue, lastDayValue, lastMonthValue, lastYearValue) = struct.unpack("<4L", self.data[14:30])
        self.currentValue = currentValue/1000
        self.lastDayValue = lastDayValue/1000
        self.lastMonthValue = lastMonthValue/1000
        self.lastYearValue = lastYearValue/1000
    
    def __str__(self):
        return f"{self._header()} | {self.currentValue:>10.3f} | {self.lastDayValue:>10.3f} | {self.lastMonthValue:>10.3f} | {self.lastYearValue:>10.3f} | {self._rest(30)}| {self._footer()}"
    
    def getData(self):
        data = super().getData()
        data['currentValue'] = self.currentValue
        data['lastDayValue'] = self.lastDayValue
        data['lastMonthValue'] = self.lastMonthValue
        data['lastYearValue'] = self.lastYearValue
        return data 


class ColdWaterMeter(WaterMeter):
    pass

class WarmWaterMeter(WaterMeter):
    pass
