import threading
import glob
import mutableObject as mo
import peripherals.specialChars as chars

class LocalDashboard():
    def __init__(self, alarmDataCenter, alarmControlCenter, lcd):
        self.taskManager = {
            #Global Vars for tasks
            "readLight" : mo.Mutable(True),
            "readTemperature" : mo.Mutable(True),
            "readHumidity" : mo.Mutable(True)
        }
        
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
        
    def show(self):
        if self.running:
            print("Dashboard already running...")
            return
        
        if not self.continueFlag.is_set():
            print("Dashboard is disabled and can't be started.")
            return
        
        print("Starting dashboard...")
        self.running = True
        
        self.lcd.lock.acquire()
        self.lcd.clear()
        self.lcd.lock.release()
            
        self.taskManager["read" + glob.stringCapitalize(glob.temperatureKey)].set(True)
        self.taskManager["read" + glob.stringCapitalize(glob.humidityKey)].set(True)
        self.taskManager["read" + glob.stringCapitalize(glob.lightKey)].set(True)
        
        thread(glob.timedRepeat, 3000, self.taskManager["read" + glob.stringCapitalize(glob.temperatureKey)], self.continueFlag,
            [
                self.dataCenter.dummy, self.displayData
            ], 
            [
                [glob.temperatureKey, -10, 40], 
                [mo.Mutable((0, 1)), (0, 0), self.lcd.CGRAM[0], glob.temperatureKey, self.dataCenter.sensorStorage[glob.temperatureKey], self.lcd.CGRAM[3]]
            ]
        )
        
        thread(glob.timedRepeat, 6000, self.taskManager["read" + glob.stringCapitalize(glob.humidityKey)], self.continueFlag,
            [   
                self.dataCenter.dummy, self.displayData, 
                self.dataCenter.dummy, self.displayData
            ], 
            [
                [glob.humidityKey, 0, 100], 
                [self.iconCharsLastWrittenPosition[glob.temperatureKey], (1, 0), self.lcd.CGRAM[1], glob.humidityKey, self.dataCenter.sensorStorage[glob.humidityKey], "%"],
                
                [glob.lightKey, 0, 100], 
                [mo.Mutable((0, 0)), (0, 0), self.lcd.CGRAM[2], glob.lightKey, self.dataCenter.sensorStorage[glob.lightKey], "%"]
            ]
        )
        
        self.displayStatus()

        print("Threads running...")
    
    def stopDashboard(self):
        print("Stopping dashboard")
        self.taskManager["read" + glob.stringCapitalize(glob.temperatureKey)].set(False)
        self.taskManager["read" + glob.stringCapitalize(glob.humidityKey)].set(False)
        self.taskManager["read" + glob.stringCapitalize(glob.lightKey)].set(False)
        self.running = False
    
    def displayData(self, xyReferenceMO, xyOffset, iconChar, key, dataMO, extraChar = "", dynamicPadding = False):
        nDecimals = self.dataCenter.decimalPos[key].get()
        shortString = (str('%.*f') % (nDecimals, dataMO.get()))
        shortString = shortString + extraChar
        
        #print("Calculating maxlength with " + str(key) + " as the key...")
        maxLength = self.dataCenter.calculateMaxLength(key)
        if (nDecimals > 0):
            maxLength = maxLength + nDecimals + 1 #tenere in considerazione il char punto
        
        self.lcd.lock.acquire() # {
        xyReference = xyReferenceMO.get()
        self.lcd.printAtPos(glob.stringRpad(iconChar + shortString, maxLength+1), xyReference[0]+xyOffset[0], xyReference[1]+xyOffset[1])
        cursorPos = self.lcd.getCursorPos()
        self.lcd.lock.release()
        # }
        
        if dynamicPadding:
            self.iconCharsLastWrittenPosition[key].set((cursorPos[0]-maxLength+len(shortString), cursorPos[1]))
        else:
            self.iconCharsLastWrittenPosition[key].set((cursorPos[0], cursorPos[1]))
            
    def displayStatus(self):
        if not self.running:
            print("Dashboard not running...")
            return
        
        if not self.continueFlag.is_set():
            print("Dashboard is disabled and can't be started.")
            return
        
        string = ""
        
        if self.controlCenter.enable["alarm"].get():
            string += self.lcd.CGRAM[4]  #EXCLAMATION
            
        string += self.lcd.CGRAM[6]
        
        if self.controlCenter.running["mqtt"].get():
            string += self.lcd.CGRAM[7] #MQTT Logo
        
        self.lcd.lock.acquire()
        self.lcd.writeCGRAM(chars.MQTT, 7) #this acts as a temp buffer
        if self.controlCenter.running["wifi"].get() == True:
            self.lcd.writeCGRAM(chars.WIFI, 6)
        else:
            self.lcd.writeCGRAM(chars.NO_SIGNAL, 6) 
        
        self.lcd.print(glob.stringLpad(string, 8), row = 0, align='RIGHT', delay = 0)
        self.lcd.lock.release()