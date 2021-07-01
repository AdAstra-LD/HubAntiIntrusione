import adc 
import threading
import glob
import utilities.circularList as cList
import utilities.cString as cString
import peripherals.specialChars as chars

class DataCenter():
    def __init__(self, mqttClient, htu21d, pinPhotoresistor, lcd, decimalTemperature = 0, decimalHumidity = 0, decimalLight = 0):
        self.mqttClient = mqttClient
        
        self.enableDataRetrieval = True
        self.enableDataSend = False
        self.enableDataShow = True
        
        self.dataRetrievalRunning = False
        self.continueFlag = threading.Event()
        self.continueFlag.set()
        
        self.htu21d = htu21d
        self.photoresistor = pinPhotoresistor
        self.lcd = lcd
        
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
        
        self.iconCharsLastWrittenPosition = { 
            glob.temperatureKey : (0, 1),
            glob.humidityKey : (0, 1),
            glob.lightKey : (0, 0)
        }
    
    def startRetrieveData(self, refreshTime, nonBlocking = False):
        if self.dataRetrievalRunning:
            print("Data retrieval already running...")
            return
        
        print("Starting Data retrieval ...")
        
        if nonBlocking:
            thread(self._bodyRetrieveData, refreshTime)
        else:
            self._bodyRetrieveData(refreshTime)
    
    def _bodyRetrieveData(self, refreshTime):
        self.dataRetrievalRunning = True
        while self.enableDataRetrieval:
            self.continueFlag.wait()
            
            print("Reading t")
            for retry in range(5):
                try:
                    t = round(self.htu21d.get_temp(), self.decimalPos[glob.temperatureKey])
                    break
                except InvalidHardwareStatusError as ihs:
                    print(ihs)
            
            print("Reading h")
            for retry in range(5):
                try:
                    h = round(self.htu21d.get_humid(), self.decimalPos[glob.humidityKey])
                    break
                except InvalidHardwareStatusError as ihs:
                    print(ihs)
                    
            l = self.readLight(invert = True)
            
            self.sensorStorage[glob.temperatureKey] = t
            self.sensorStorage[glob.humidityKey] = h
            self.sensorStorage[glob.lightKey] = l
            
            self.sensorHistory[glob.temperatureKey].add(t)
            self.sensorHistory[glob.humidityKey].add(h)
            self.sensorHistory[glob.lightKey].add(l)
            
            if self.enableDataSend:
                try:
                    self.mqttClient.publish(str(glob.topicRoot + '/' + glob.temperatureKey), str(t), 1) 
                    self.mqttClient.publish(str(glob.topicRoot + '/' + glob.humidityKey), str(h), 1)
                    self.mqttClient.publish(str(glob.topicRoot + '/' + glob.lightKey), str(l), 1) 
                    
                    self.mqttClient.publish(str(glob.topicRoot + '/H' + glob.temperatureKey), str(self.sensorHistory[glob.temperatureKey]), 1) 
                    self.mqttClient.publish(str(glob.topicRoot + '/H' + glob.humidityKey), str(self.sensorHistory[glob.humidityKey]), 1) 
                    self.mqttClient.publish(str(glob.topicRoot + '/H' + glob.lightKey), str(self.sensorHistory[glob.lightKey]), 1) 
                except Exception as e:
                    print("Error" + str(e))
                    sleep(100)
            
            if self.enableDataShow:
                self.lcd.lock.acquire()
                self.displayData((0, 0), (0, 0), self.lcd.CGRAM[2], glob.lightKey, self.sensorStorage[glob.lightKey], "%")
                self.displayData((0, 1), (0, 0), self.lcd.CGRAM[0], glob.temperatureKey, self.sensorStorage[glob.temperatureKey], self.lcd.CGRAM[3])
                self.displayData(self.iconCharsLastWrittenPosition[glob.temperatureKey], (1, 0), self.lcd.CGRAM[1], glob.humidityKey, self.sensorStorage[glob.humidityKey], "%")
                self.lcd.lock.release()
     
            sleep(refreshTime)
            
        print("DataRetrieval process killed")
        
    def displayData(self, xyReference, xyOffset, iconChar, key, data, extraChar = ""):
        #NOT THREAD SAFE.
        #REMEMBER TO ACQUIRE LOCK ON LCD DISPLAY BEFORE CALLING this
        WHITESPACE_AMOUNT = 1
        
        nDecimals = self.decimalPos[key]
        shortString = (str('%.*f') % (nDecimals, data))
        shortString = shortString + extraChar
        
        #print("Calculating maxlength with " + str(key) + " as the key...")
        
        maxLength = 1 + max(len(str(self.dataRanges[key][0])), len(str(self.dataRanges[key][1]))) #icona + max numero di Cifre intere e segno
        if nDecimals > 0:
            maxLength = maxLength + nDecimals + 1 #tenere in considerazione il char punto
        
        # {
        self.lcd.printAtPos(cString.rpad(iconChar + shortString, maxLength+WHITESPACE_AMOUNT), xyReference[0]+xyOffset[0], xyReference[1]+xyOffset[1])
        cursorPos = self.lcd.getCursorPos()
        # }
        
        self.iconCharsLastWrittenPosition[key] = (cursorPos[0]-WHITESPACE_AMOUNT, cursorPos[1])
    
    
    
    def readLight(self, invert = False):
        valore = adc.read(self.photoresistor)
        
        if invert:
            valore = 4095 - valore
        
        percentage = round(100*valore/4095, self.decimalPos[glob.lightKey])
        return percentage
        
    #def dummyVal(self, key, lowerLimit, upperLimit):
    #    val = random(lowerLimit, upperLimit*17)
    #    val = val/17
    #    self.sensorStorage[key] = val
    #    return val