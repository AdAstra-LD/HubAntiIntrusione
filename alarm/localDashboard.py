import threading
import glob
import utilities.cString as cString
import utilities.mutableObject as mo
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
            glob.temperatureKey : mo.Mutable((0, 1)),
            glob.humidityKey : mo.Mutable((0, 1)),
            glob.lightKey : mo.Mutable((0, 0))
        }
    
    def _dashboard_bodyrun(self, refreshTime):
        self.running = True
        while self.enable:
            self.continueFlag.wait()
            
            self.dataCenter.sensoreStorageLock.acquire()
            self.lcd.lock.acquire()
            self.displayData(mo.Mutable((0, 0)), (0, 0), self.lcd.CGRAM[2], glob.lightKey, self.dataCenter.sensorStorage[glob.lightKey], "%")
            self.displayData(mo.Mutable((0, 1)), (0, 0), self.lcd.CGRAM[0], glob.temperatureKey, self.dataCenter.sensorStorage[glob.temperatureKey], self.lcd.CGRAM[3])
            self.displayData(self.iconCharsLastWrittenPosition[glob.temperatureKey], (1, 0), self.lcd.CGRAM[1], glob.humidityKey, self.dataCenter.sensorStorage[glob.humidityKey], "%")
            self.lcd.lock.release()
            
            self.dataCenter.sensoreStorageLock.release()
            
            self.displayStatus()
            sleep(refreshTime)
            
        print("Dashboard killed")
        
    def show(self, refreshTime):
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
        
        thread(self._dashboard_bodyrun, refreshTime)
        print("Thread running...")
    
    def stopDashboard(self):
        print("Stopping dashboard")
        self.taskManager["read" + cString.capitalize(glob.temperatureKey)].set(False)
        self.taskManager["read" + cString.capitalize(glob.humidityKey)].set(False)
        self.taskManager["read" + cString.capitalize(glob.lightKey)].set(False)
        self.running = False
    
    def displayData(self, xyReferenceMO, xyOffset, iconChar, key, dataMO, extraChar = "", dynamicPadding = False):
        #NOT THREAD SAFE.
        #REMEMBER TO ACQUIRE LOCK ON LCD DISPLAY BEFORE CALLING this
        WHITESPACE_AMOUNT = 1
        
        nDecimals = self.dataCenter.decimalPos[key].get()
        shortString = (str('%.*f') % (nDecimals, dataMO.get()))
        shortString = shortString + extraChar
        
        #print("Calculating maxlength with " + str(key) + " as the key...")
        maxLength = self.dataCenter.calculateMaxLength(key)
        if (nDecimals > 0):
            maxLength = maxLength + nDecimals + 1 #tenere in considerazione il char punto
        
        # {
        xyReference = xyReferenceMO.get()
        self.lcd.printAtPos(cString.rpad(iconChar + shortString, maxLength+WHITESPACE_AMOUNT), xyReference[0]+xyOffset[0], xyReference[1]+xyOffset[1])
        cursorPos = self.lcd.getCursorPos()
        # }
        
        if dynamicPadding:
            self.iconCharsLastWrittenPosition[key].set((cursorPos[0]-maxLength+len(shortString), cursorPos[1]))
        else:
            self.iconCharsLastWrittenPosition[key].set((cursorPos[0]-WHITESPACE_AMOUNT, cursorPos[1]))
            
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