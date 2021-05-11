import threading

temperDigits = 2
humidDigits = 2
lcdLock = threading.Lock()

def showTemperature(lcd, temperature, CGRAMcharPos = 0, celsiusSymbolPos = 3):
    lcdLock.acquire()
    
    lcd.printAtPos(lcd.CGRAMchar[CGRAMcharPos], 0, 0) #Temperature Symbol
    #READ ACTUAL TEMPERATURE!!!
    
    tempString = str(temperature)
    
    global temperDigits
    temperDigits = len(tempString)
    
    lcd.print(tempString) #ex.: 35 °C
    lcd.print(lcd.CGRAMchar[celsiusSymbolPos])
    lcdLock.release()
    
def showHumidity(lcd, humidity, CGRAMcharPos = 1):
    lcdLock.acquire()
    
    lcd.printAtPos(lcd.CGRAMchar[CGRAMcharPos], 3 + temperDigits, 0)
    
    humidString = str(humidity)
    global humidDigits
    humidDigits = len(humidString)
    
    lcd.print(humidString + "%") #ex. 46%
    lcdLock.release()
    
def showLight(lcd, light, CGRAMcharPos = 2):
    lcdLock.acquire()
    
    lcd.printAtPos(lcd.CGRAMchar[CGRAMcharPos], 0, 1)
    
    lightString = str(light)
    #global lightDigits
    #humidDigits = len(str(humidity))
    
    lcd.print(lightString + "%") #ex. 46%
    lcdLock.release()

def showStatus(lcd, wifiStatus, lockedStatus):
    lcdLock.acquire()
    
    #lcd.printAtPos(lcd.CGRAMchar[CGRAMcharPos], 0, 1)
    
    lcdLock.release()