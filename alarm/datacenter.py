import adc 
import utilities.mutableObject as mo
import threading
import glob

class DataCenter():
    def __init__(self, decimalTemperature = 0, decimalHumidity = 0, decimalLight = 0):
        self.sensoreStorageLock = threading.Lock()
        self.sensorStorage = { 
            glob.temperatureKey : mo.Mutable(0.0),
            glob.humidityKey : mo.Mutable(0.0),
            glob.lightKey : mo.Mutable(0)
        }
        
        self.dataRanges = { 
            glob.temperatureKey : (-99, 99),
            glob.humidityKey : (0, 100),
            glob.lightKey : (0, 100)
        }
        
        self.decimalPos = { 
            glob.temperatureKey : mo.Mutable(decimalTemperature),
            glob.humidityKey : mo.Mutable(decimalHumidity),
            glob.lightKey : mo.Mutable(decimalLight)
        }
    
    def calculateMaxLength(self, key):
        return 1 + max(len(str(self.dataRanges[key][0])), len(str(self.dataRanges[key][1]))) #icona + maxCifre intere + eventuale segno
    
    def readTemperature(self, htu):
        t = htu.get_temp()
        self.sensorStorage[glob.temperatureKey].set(t)
        return t# Read raw temperature
    
    def readHumidity(self, htu):
        h = htu.get_humid()
        self.sensorStorage[glob.humidityKey].set(h)
        return h # Read raw temperature
    
    def readLight(self, pinSensor, invert = False):
        valore = adc.read(pinSensor)
        
        if invert:
            valore = 4096 - valore
        
        percentage = round(100*valore/4095)
        
        self.sensorStorage[glob.lightKey] = percentage
        return percentage
        
    def dummy(self, lowerLimit, upperLimit):
        val = random(lowerLimit, upperLimit*17)
        val = val/17
        self.sensorStorage[glob.lightKey].set(val)
        return self.sensorStorage[glob.lightKey].get()