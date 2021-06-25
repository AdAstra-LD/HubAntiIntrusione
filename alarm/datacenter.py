import adc 
import mutableObject as mo

sensorStorage = { 
    "light" : mo.Mutable(0),
    "temperature" : mo.Mutable(0.0),
    "humidity" : mo.Mutable(0.0)
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
    sensorStorage["light"].set(val)
    return sensorStorage["light"].get()