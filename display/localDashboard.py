import threading
import alarm.datacenter as datacenter
import glob

def showDashboard(lcd):
    glob.lcdLock.acquire()
    lcd.clear()
    glob.lcdLock.release()
    
    thread(glob.timedRepeat, 3000, glob.enable["readLight"], 
        (datacenter.dummy, showLight), 
        ((), (lcd, datacenter.sensorStorage["light"]),))
        
    #thread(glob.timedRepeat, 15000, glob.enable["readLight"], datacenter.readAmbientLight, (glob.photoresistor, True))
    #thread(glob.timedRepeat, 15000, glob.enable["readTemperature"], datacenter.readTemperature, (I2C???, 2))
    #thread(glob.timedRepeat, 15000, glob.enable["readHumidity"], datacenter.readHumidity, (I2C???, 2))

def showTemperature(lcd, temperature, CGRAMcharPos = 0, celsiusSymbolPos = 3):
    glob.lcdLock.acquire()
    
    lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 0, 0) #Temperature Symbol 
    
    #print value
    tempString = str(temperature)
    
    global temperDigits
    temperDigits = len(tempString)
    
    lcd.print(tempString) #ex.: 35 °C
    lcd.print(lcd.CGRAM[celsiusSymbolPos])
    glob.lcdLock.release()
    
def showHumidity(lcd, humidity, CGRAMcharPos = 1):
    glob.lcdLock.acquire()
    
    lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 3 + temperDigits, 0)
    
    #print value
    humidString = str(humidity)
    global humidDigits
    humidDigits = len(humidString)
    
    lcd.print(humidString + "%") #ex. 46%
    glob.lcdLock.release()
    
def showLight(lcd, light, CGRAMcharPos = 2):
    glob.lcdLock.acquire()
    
    lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 0, 1)
    
    #print value
    lightString = str(light)    
    lcd.print(lightString + "%") #ex. 46%
    glob.lcdLock.release()

def showStatus(lcd, wifiStatus, lockedStatus):
    glob.lcdLock.acquire()
    
    #lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 0, 1)
    
    glob.lcdLock.release()