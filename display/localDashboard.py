import threading

import glob

def showTemperature(lcd, temperature, CGRAMcharPos = 0, celsiusSymbolPos = 3):
    glob.lcdLock.acquire()
    
    glob.lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 0, 0) #Temperature Symbol 
    
    #print value
    tempString = str(temperature)
    
    global temperDigits
    temperDigits = len(tempString)
    
    glob.lcd.print(tempString) #ex.: 35 °C
    glob.lcd.print(lcd.CGRAM[celsiusSymbolPos])
    glob.lcdLock.release()
    
def showHumidity(lcd, humidity, CGRAMcharPos = 1):
    glob.lcdLock.acquire()
    
    glob.lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 3 + temperDigits, 0)
    
    #print value
    humidString = str(humidity)
    global humidDigits
    humidDigits = len(humidString)
    
    glob.lcd.print(humidString + "%") #ex. 46%
    glob.lcdLock.release()
    
def showLight(lcd, light, CGRAMcharPos = 2):
    glob.lcdLock.acquire()
    
    glob.lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 0, 1)
    
    #print value
    lightString = str(light)    
    glob.lcd.print(lightString + "%") #ex. 46%
    glob.lcdLock.release()

def showStatus(lcd, wifiStatus, lockedStatus):
    glob.lcdLock.acquire()
    
    #glob.lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 0, 1)
    
    glob.lcdLock.release()