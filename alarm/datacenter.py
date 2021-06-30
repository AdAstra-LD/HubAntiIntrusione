import adc 
import threading
import glob
import utilities.circularList as cList

class DataCenter():
    def __init__(self, alarmCommunicationCenter, htu21d, decimalTemperature = 0, decimalHumidity = 0, decimalLight = 0):
        self.commCenter = alarmCommunicationCenter
        
        self.enableDataSend = True
        self.enableDataRetrieval = True
        self.dataRetrievalRunning = False
        self.continueFlag = threading.Event()
        self.continueFlag.set()
        
        self.htu21d = htu21d
        
        self.sensoreStorageLock = threading.Lock()
        
        self.sensorStorage = { 
            glob.temperatureKey : 0.0,
            glob.humidityKey : 0.0,
            glob.lightKey : 0.0
        }
        
        self.sensorHistory = { 
            glob.temperatureKey : cList.CircularNumericList(),
            glob.humidityKey : cList.CircularNumericList(),
            glob.lightKey : cList.CircularNumericList()
        }
        
        self.dataRanges = { 
            glob.temperatureKey : (-99, 99),
            glob.humidityKey : (0, 100),
            glob.lightKey : (0, 100)
        }
        
        self.decimalPos = { 
            glob.temperatureKey : decimalTemperature,
            glob.humidityKey : decimalHumidity,
            glob.lightKey : decimalLight
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
            
            self.sensorStorage[glob.temperatureKey] = self.htu21d.get_temp()
            self.sensorHistory[glob.temperatureKey].add(self.sensorStorage[glob.temperatureKey], self.decimalPos[glob.temperatureKey])
            
            self.sensorStorage[glob.humidityKey] = self.htu21d.get_humid()
            self.sensorHistory[glob.humidityKey].add(self.sensorStorage[glob.humidityKey], self.decimalPos[glob.humidityKey])
            
            l = self.dummy(0, 100)
            
            if self.enableDataSend:
                try:
                    nDecimalsT = self.decimalPos[glob.temperatureKey]
                    nDecimalsH = self.decimalPos[glob.humidityKey]
                    nDecimalsL = self.decimalPos[glob.lightKey]
                    
                    self.commCenter.mqttClient.publish(str("roomIOT2021" + '/' + glob.temperatureKey), str('%.*f') % (nDecimalsT, self.sensorStorage[glob.temperatureKey]), 1) 
                    self.commCenter.mqttClient.publish(str("roomIOT2021" + '/' + glob.humidityKey), str('%.*f') % (nDecimalsH, self.sensorStorage[glob.humidityKey]), 1)
                    self.commCenter.mqttClient.publish(str("roomIOT2021" + '/' + glob.lightKey), str('%.*f') % (nDecimalsL, l), 1) 
                    
                    self.commCenter.mqttClient.publish(str("roomIOT2021" + '/H' + glob.temperatureKey), str(self.sensorHistory[glob.temperatureKey]), 1) 
                    self.commCenter.mqttClient.publish(str("roomIOT2021" + '/H' + glob.humidityKey), str(self.sensorHistory[glob.humidityKey]), 1) 
                    self.commCenter.mqttClient.publish(str("roomIOT2021" + '/H' + glob.lightKey), str(self.sensorHistory[glob.lightKey]), 1) 
                except Exception as e:
                    print("Error" + str(e))
                    sleep(100)
                    
            self.sensoreStorageLock.release()
            sleep(refreshTime)
            
        print("DataRetrieval process killed")
    
    #def readLight(self, pinSensor, invert = False):
    #    valore = adc.read(pinSensor)
    #    
    #    if invert:
    #        valore = 4096 - valore
    #    
    #    percentage = round(100*valore/4095)
    #    
    #    self.sensorStorage[glob.lightKey] = percentage
    #    return percentage
        
    def dummy(self, lowerLimit, upperLimit):
        val = random(lowerLimit, upperLimit*17)
        val = val/17
        self.sensorStorage[glob.lightKey] = val
        self.sensorHistory[glob.lightKey].add(val, self.decimalPos[glob.lightKey])
        return val