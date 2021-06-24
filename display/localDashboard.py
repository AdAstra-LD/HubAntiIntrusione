import threading
import adc

import glob

sensorStorage = { }

def readTemperature(i2c, temperDigits = 2, timePeriod = 15000):
    pass

def readHumidity(i2c, humidDigits = 2, timePeriod = 15000):
    pass

def readLight(pinPhotoresist, invert = False, keyName = "light"):
    valore = adc.read(pinPhotoresist)
    
    if invert:
        valore = 4096 - valore
    
    valore = round(100*valore/4095)
    
    sensorStorage[keyName] = valore
    return valore #Percentage

def showTemperature(lcd, temperature, CGRAMcharPos = 0, celsiusSymbolPos = 3):
    glob.lcdLock.acquire()
    
    glob.lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 0, 0) #Temperature Symbol
    #READ ACTUAL TEMPERATURE!!!
    
    
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
    
    lightString = str(light)
    #global lightDigits
    #humidDigits = len(str(humidity))
    
    glob.lcd.print(lightString + "%") #ex. 46%
    glob.lcdLock.release()

def showStatus(lcd, wifiStatus, lockedStatus):
    glob.lcdLock.acquire()
    
    #glob.lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 0, 1)
    
    glob.lcdLock.release()