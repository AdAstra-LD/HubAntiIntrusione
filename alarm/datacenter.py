import adc 

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