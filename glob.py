import threading

#Global Vars
alarmEnable = False;
audioEnable = True;
flashEnable = True;

#Global Vars for tasks
enable_readAmbientLight = True
enable_readTemperature = True
enable_readHumidity = True

#Lock objects for threading
lcdLock = threading.Lock()

#Peripherals
lcd = None
pad = None
ledRGB = None

#Utilities
def isNumber(s):
    if s == None:
        return False
        
    try:
        int(s)
        return True
    except ValueError:
        return False
        
def pinToggleMulti (*args):
    for pin in args:
        pinToggle(pin)

def flashPins(flashFrequency, *args):
    if (flashFrequency == 0):
        flashFrequency = 1
    
    thread(timedRepeat, 1000//flashFrequency, flashEnable, pinToggleMulti, *args)

def timedRepeat(timePeriod, runCondition, task, *args):
    while runCondition:
        task(*args)
        sleep(timePeriod)
