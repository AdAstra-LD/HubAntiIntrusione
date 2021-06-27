import adc 
import mutableObject as mo

temperatureKey = 'temperature'
humidityKey = 'humidity'
lightKey = 'light'

sensorStorage = { 
    temperatureKey : mo.Mutable(0.0),
    humidityKey : mo.Mutable(0.0),
    lightKey : mo.Mutable(0)
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
    
def dummy(keyName, lowerLimit, upperLimit):
    global sensorStorage
    
    val = random(lowerLimit, upperLimit*17)
    val = val/17
    sensorStorage[keyName].set(val)
    return sensorStorage[keyName].get()