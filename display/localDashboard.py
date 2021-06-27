import threading
import alarm.datacenter as datacenter
import glob
import mutableObject as mo

iconsLastWrittenPosition = { 
    datacenter.temperatureKey : mo.Mutable((0, 0)),
    datacenter.humidityKey : mo.Mutable((0, 0)),
    datacenter.lightKey : mo.Mutable((0, 0))
}

dataRange = { 
    datacenter.temperatureKey : (-99, 99),
    datacenter.humidityKey : (0, 100),
    datacenter.lightKey : (0, 100)
}

decimalPos = { 
    datacenter.temperatureKey : mo.Mutable(1),
    datacenter.humidityKey : mo.Mutable(1),
    datacenter.lightKey : mo.Mutable(0)
}

def showDashboard(lcd):
    lcd.lock.acquire()
    lcd.clear()
    lcd.lock.release()
    
    thread(glob.timedRepeat, 1100, glob.enable["read" + glob.stringCapitalize(datacenter.temperatureKey)], 
        (datacenter.dummy, displayData), 
        ([datacenter.temperatureKey, -10, 40], [lcd, mo.Mutable((0, 1)), (0, 0), lcd.CGRAM[0], datacenter.temperatureKey, datacenter.sensorStorage[datacenter.temperatureKey], lcd.CGRAM[3]]))
    
    thread(glob.timedRepeat, 9000, glob.enable["read" + glob.stringCapitalize(datacenter.humidityKey)], 
        (datacenter.dummy, displayData), 
        ([datacenter.humidityKey, 0, 100], [lcd, iconsLastWrittenPosition[datacenter.temperatureKey], (1, 0), lcd.CGRAM[1], datacenter.humidityKey, datacenter.sensorStorage[datacenter.humidityKey], "%"]))
        
    thread(glob.timedRepeat, 1250, glob.enable["read" + glob.stringCapitalize(datacenter.lightKey)], 
        (datacenter.dummy, displayData), 
        ([datacenter.lightKey, 0, 100], [lcd, mo.Mutable((0, 0)), (0, 0), lcd.CGRAM[2], datacenter.lightKey, datacenter.sensorStorage[datacenter.lightKey], "%"]))


def displayData(lcd, xyReferenceMO, xyOffset, icon, key, dataMO, extraChar = "", dynamicPadding = False):
    lcd.lock.acquire()

    xyReference = xyReferenceMO.get()
    nDecimals = decimalPos[key].get()
    
    #Print Temperature Symbol 
    lcd.printAtPos(icon, xyReference[0]+xyOffset[0], xyReference[1]+xyOffset[1]) 
    
    shortString = (str('%.*f') % (nDecimals, dataMO.get()))
    shortString = shortString + extraChar
    
    maxLength = 1 + max(len(str(dataRange[key][0])), len(str(dataRange[key][1]))) #icona + maxCifre intere + eventuale segno
    if (nDecimals > 0):
        maxLength = maxLength + nDecimals + 1 #tenere in considerazione il punto
        
    lcd.print(glob.stringRpad(shortString, maxLength)) #1 per segno, 2 per cifre intere, 1 per punto, decimali, 1 per spazio
    
    cursorPos = lcd.getCursorPos()
    if dynamicPadding:
        iconsLastWrittenPosition[key].set((cursorPos[0]-maxLength+len(shortString), cursorPos[1]))
    else:
        iconsLastWrittenPosition[key].set((cursorPos[0], cursorPos[1]))
    
    lcd.lock.release()
    
def showStatus(lcd, wifiStatus, lockedStatus):
    lcd.lock.acquire()
    
    #lcd.printAtPos(lcd.CGRAM[CGRAMcharPos], 0, 1)
    
    lcd.lock.release()