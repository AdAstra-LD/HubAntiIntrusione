import adc 
import utilities.mutableObject as mo
import threading
import glob

class DataCenter():
    def __init__(self, htu21d, decimalTemperature = 0, decimalHumidity = 0, decimalLight = 0):
        self.enableDataRetrieval = True
        self.dataRetrievalRunning = False
        self.continueFlag = threading.Event()
        self.continueFlag.set()
        
        self.htu21d = htu21d
        
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
    
    def startRetrieveData(self, refreshTime):
        if self.dataRetrievalRunning:
            print("Data retrieval already running...")
            return
        
        print("Starting Data retrieval ...")
        
        thread(self._bodyRetrieveData, refreshTime)
    
    def _bodyRetrieveData(self, refreshTime):
        self.dataRetrievalRunning = True
        while self.enableDataRetrieval:
            self.continueFlag.wait()
            
            self.sensoreStorageLock.acquire()
            
            self.dummy(0, 100)
            self.readTemperature(self.htu21d)
            self.readHumidity(self.htu21d)
            
            self.sensoreStorageLock.release()
            sleep(refreshTime)
            
        print("DataRetrieval process killed")
        
    
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