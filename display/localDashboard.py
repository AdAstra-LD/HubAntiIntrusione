import threading

temperDigits = 2
humidDigits = 2
lcdLock = threading.Lock()

def showTemperature(lcd, temperature, CGRAMcharPos = 0, celsiusSymbolPos = 3):
    lcdLock.acquire()
    
    lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 0, 0) #Temperature Symbol
    #READ ACTUAL TEMPERATURE!!!
    
    
    #print value
    tempString = str(temperature)
    
    global temperDigits
    temperDigits = len(tempString)
    
    lcd.print(tempString) #ex.: 35 °C
    lcd.print(lcd.CGRAM[celsiusSymbolPos])
    lcdLock.release()
    
def showHumidity(lcd, humidity, CGRAMcharPos = 1):
    lcdLock.acquire()
    
    lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 3 + temperDigits, 0)
    
    
    #print value
    humidString = str(humidity)
    global humidDigits
    humidDigits = len(humidString)
    
    lcd.print(humidString + "%") #ex. 46%
    lcdLock.release()
    
def showLight(lcd, light, CGRAMcharPos = 2):
    lcdLock.acquire()
    
    lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 0, 1)
    
    
    #print value
    lightString = str(light)
    #global lightDigits
    #humidDigits = len(str(humidity))
    
    lcd.print(lightString + "%") #ex. 46%
    lcdLock.release()

def showStatus(lcd, wifiStatus, lockedStatus):
    lcdLock.acquire()
    
    #lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 0, 1)
    
    lcdLock.release()