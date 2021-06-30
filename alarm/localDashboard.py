import threading
import glob
import utilities.cString as cString
import peripherals.specialChars as chars

class LocalDashboard():
    def __init__(self, alarmDataCenter, alarmControlCenter, lcd):
        self.enable = True
        self.running = False
        self.continueFlag = threading.Event()
        self.continueFlag.set()
        
        self.lcd = lcd
        self.dataCenter = alarmDataCenter
        self.controlCenter = alarmControlCenter
        
        self.iconCharsLastWrittenPosition = { 
            glob.temperatureKey : (0, 1),
            glob.humidityKey : (0, 1),
            glob.lightKey : (0, 0)
        }
    
    def _dashboard_bodyrun(self, refreshTime):
        self.running = True
        while self.enable:
            self.continueFlag.wait()
            
            self.dataCenter.sensoreStorageLock.acquire()
            
            self.lcd.lock.acquire()
            self.displayData((0, 0), (0, 0), self.lcd.CGRAM[2], glob.lightKey, self.dataCenter.sensorStorage[glob.lightKey], "%")
            self.displayData((0, 1), (0, 0), self.lcd.CGRAM[0], glob.temperatureKey, self.dataCenter.sensorStorage[glob.temperatureKey], self.lcd.CGRAM[3])
            self.displayData(self.iconCharsLastWrittenPosition[glob.temperatureKey], (1, 0), self.lcd.CGRAM[1], glob.humidityKey, self.dataCenter.sensorStorage[glob.humidityKey], "%")
            self.lcd.lock.release()
            
            self.dataCenter.sensoreStorageLock.release()
            
            self.displayStatus()
            sleep(refreshTime)
            
        print("Dashboard killed")
        
    def show(self, refreshTime, nonBlocking = False):
        if self.running:
            print("Dashboard already running...")
            return
        
        if not self.continueFlag.is_set():
            print("Dashboard is disabled and can't be started.")
            return
        
        print("Starting dashboard...")
        
        self.lcd.lock.acquire()
        self.lcd.clear()
        self.lcd.lock.release()
        
        if nonBlocking:
            thread(self._dashboard_bodyrun, refreshTime)
            print("Dashboard running in separate thread")
        else:
            self._dashboard_bodyrun(refreshTime)
    
    def stopDashboard(self):
        print("Stopping dashboard")
        self.enable = False
        self.running = False
    
    def displayData(self, xyReference, xyOffset, iconChar, key, data, extraChar = "", dynamicPadding = False):
        #NOT THREAD SAFE.
        #REMEMBER TO ACQUIRE LOCK ON LCD DISPLAY BEFORE CALLING this
        WHITESPACE_AMOUNT = 1
        
        nDecimals = self.dataCenter.decimalPos[key]
        shortString = (str('%.*f') % (nDecimals, data))
        shortString = shortString + extraChar
        
        #print("Calculating maxlength with " + str(key) + " as the key...")
        
        maxLength = 1 + max(len(str(self.dataCenter.dataRanges[key][0])), len(str(self.dataCenter.dataRanges[key][1]))) #icona + max numero di Cifre intere e segno
        if nDecimals > 0:
            maxLength = maxLength + nDecimals + 1 #tenere in considerazione il char punto
        
        # {
        self.lcd.printAtPos(cString.rpad(iconChar + shortString, maxLength+WHITESPACE_AMOUNT), xyReference[0]+xyOffset[0], xyReference[1]+xyOffset[1])
        cursorPos = self.lcd.getCursorPos()
        # }
        
        if dynamicPadding:
            self.iconCharsLastWrittenPosition[key] = (cursorPos[0]-maxLength+len(shortString), cursorPos[1])
        else:
            self.iconCharsLastWrittenPosition[key] = (cursorPos[0]-WHITESPACE_AMOUNT, cursorPos[1])
            
    def displayStatus(self):
        if not self.running:
            print("Dashboard not running...")
            return
        
        if not self.continueFlag.is_set():
            print("Dashboard is disabled and can't be started.")
            return
        
        string = ""
        
        if self.controlCenter.enableAlarm:
            string += self.lcd.CGRAM[4]  #EXCLAMATION
            
        string += self.lcd.CGRAM[6]
        
        if self.controlCenter.commCenter.running["mqtt"]:
            string += self.lcd.CGRAM[7] #MQTT Logo
        
        self.lcd.lock.acquire()
        self.lcd.writeCGRAM(chars.MQTT, 7) #this acts as a temp buffer
        if self.controlCenter.commCenter.running["wifi"]:
            self.lcd.writeCGRAM(chars.WIFI, 6)
        else:
            self.lcd.writeCGRAM(chars.NO_SIGNAL, 6) 
        
        self.lcd.print(cString.lpad(string, 8), row = 0, align='RIGHT', delay = 0)
        self.lcd.lock.release()