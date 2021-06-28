import threading
import glob
import mutableObject as mo

class LocalDashboard():
    def __init__(self, alarmDataCenter, lcd, ext_enable = None):
        self.enable = {
            #Global Vars for tasks
            "general" : mo.Mutable(False),
            "readLight" : mo.Mutable(True),
            "readTemperature" : mo.Mutable(True),
            "readHumidity" : mo.Mutable(True)
        }
        
        self.lcd = lcd
        self.dataCenter = alarmDataCenter
        self.ext_enable = ext_enable
        
        self.iconsLastWrittenPosition = { 
            glob.temperatureKey : mo.Mutable((0, 1)),
            glob.humidityKey : mo.Mutable((0, 1)),
            glob.lightKey : mo.Mutable((0, 0))
        }
        
    def show(self):
        if self.enable["general"].get() == True:
            print("Dashboard already running...")
            return
        
        print("Starting dashboard...")
        
        self.lcd.lock.acquire()
        self.lcd.clear()
        self.lcd.lock.release()
        print("lcd cleared...")
            
        self.enable["read" + glob.stringCapitalize(glob.temperatureKey)].set(True)
        self.enable["read" + glob.stringCapitalize(glob.humidityKey)].set(True)
        self.enable["read" + glob.stringCapitalize(glob.lightKey)].set(True)
        print("Control signals enabled...")
        
        self.enable["general"].set(True)
        
        thread(glob.timedRepeat, 1500, self.enable["read" + glob.stringCapitalize(glob.temperatureKey)], 
            (self.dataCenter.dummy, self.displayData), 
            ([glob.temperatureKey, -10, 40], [mo.Mutable((0, 1)), (0, 0), self.lcd.CGRAM[0], glob.temperatureKey, self.dataCenter.sensorStorage[glob.temperatureKey], self.lcd.CGRAM[3]]),
            self.ext_enable)
        
        thread(glob.timedRepeat, 5000, self.enable["read" + glob.stringCapitalize(glob.humidityKey)], 
            (self.dataCenter.dummy, self.displayData), 
            ([glob.humidityKey, 0, 100], [self.iconsLastWrittenPosition[glob.temperatureKey], (1, 0), self.lcd.CGRAM[1], glob.humidityKey, self.dataCenter.sensorStorage[glob.humidityKey], "%"]))
            
        thread(glob.timedRepeat, 5000, self.enable["read" + glob.stringCapitalize(glob.lightKey)], 
            (self.dataCenter.dummy, self.displayData), 
            ([glob.lightKey, 0, 100], [mo.Mutable((0, 0)), (0, 0), self.lcd.CGRAM[2], glob.lightKey, self.dataCenter.sensorStorage[glob.lightKey], "%"]))
        
        print("Threads running...")
    
    def stopDashboard(self):
        print("Stopping dashboard")
        self.enable["read" + glob.stringCapitalize(glob.temperatureKey)].set(False)
        self.enable["read" + glob.stringCapitalize(glob.humidityKey)].set(False)
        self.enable["read" + glob.stringCapitalize(glob.lightKey)].set(False)
        self.enable["general"].set(False)
    
    def displayData(self, xyReferenceMO, xyOffset, icon, key, dataMO, extraChar = "", dynamicPadding = False):
        print(str(self.dataCenter.decimalPos) + " " + str(key))
        print(self.dataCenter.decimalPos[key])
        nDecimals = self.dataCenter.decimalPos[key].get()
        shortString = (str('%.*f') % (nDecimals, dataMO.get()))
        shortString = shortString + extraChar
        
        print("Calculating maxlength with " + str(key) + " as the key...")
        maxLength = self.dataCenter.calculateMaxLength(key)
        if (nDecimals > 0):
            maxLength = maxLength + nDecimals + 1 #tenere in considerazione il punto
        
        print("Requesting lcd print...")
        self.lcd.lock.acquire() # {
        xyReference = xyReferenceMO.get()
        self.lcd.printAtPos(glob.stringRpad(icon + shortString, maxLength+1), xyReference[0]+xyOffset[0], xyReference[1]+xyOffset[1])
        cursorPos = self.lcd.getCursorPos()
        self.lcd.lock.release()
        # }
        
        if dynamicPadding:
            self.iconsLastWrittenPosition[key].set((cursorPos[0]-maxLength+len(shortString), cursorPos[1]))
        else:
            self.iconsLastWrittenPosition[key].set((cursorPos[0], cursorPos[1]))
            
    def showStatus(self, wifiStatus, lockedStatus):
        pass