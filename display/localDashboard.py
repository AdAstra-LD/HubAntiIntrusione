import threading

temperDigits = 2
humidDigits = 2
lcdLock = threading.Lock()

def showTemperature(lcd):
    lcdLock.acquire()
    
    lcd.printAtPos(lcd.CGRAMchar[3], 0, 0) #Temperature Symbol
    temperature = 0 #READ ACTUAL TEMPERATURE!!!
    
    global temperDigits
    temperDigits = len(str(temperature))
    
    lcd.print(temperature + lcd.CGRAMchar[5]) #ex.: 35 °C
    lcdLock.release()
    
def showHumidity(lcd):
    lcdLock.acquire()
    
    lcd.printAtPos(lcd.CGRAMchar[4], 3 + temperDigits, 0)
    humidity = 0 #READ ACTUAL HUMIDITY!!!
    
    global humidDigits
    humidDigits = len(str(humidity))
    
    lcd.print(humidity + "%") #ex. 46%
    lcdLock.release()
    
def showLight(lcd, light):
    lcdLock.acquire()
    
    lcd.printAtPos(lcd.CGRAMchar[4], 0, 1)
    humidity = 0 #READ ACTUAL HUMIDITY!!!
    
    #global lightDigits
    #humidDigits = len(str(humidity))
    
    lcd.print(humidity + "%") #ex. 46%
    lcdLock.release()