import adc 

sensorStorage = { 
    "light" : 0,
    "temperature" : 0.0,
    "humidity" : 0.0
}

def readTemperature(i2c, temperDigits = 2):
    global sensorStorage
    pass

def readHumidity(i2c, humidDigits = 2):
    global sensorStorage
    pass

def readLight(pinSensor, invert = False, keyName = "light"):
    global sensorStorage
    valore = adc.read(pinSensor)
    
    if invert:
        valore = 4096 - valore
    
    percentage = round(100*valore/4095)
    
    sensorStorage[keyName] = percentage
    return percentage
    
def dummy():
    global sensorStorage
    
    val = random(0, 100)
    sensorStorage["light"] = val
    print(sensorStorage["light"])
    return val