import threading

enable = { 
    #Global Vars for system 
    "alarm" : [False],
    "audio" : [True],
    "flash" : [False],
    
    #Global Vars for tasks
    "readAmbientLight" : [True],
    "readTemperature" : [True],
    "readHumidity" : [True]
}

#Lock objects for threading
lcdLock = threading.Lock()

#Peripherals
lcd = None
pad = None
buzzer = None
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

def flashPins(flashFrequency, taskOnEnd = None, *args):
    global enable 
    global ledRGB
    
    if (flashFrequency == 0):
        flashFrequency = 1
    
    thread(timedRepeat, 1000//flashFrequency, enable["flash"], pinToggleMulti, taskOnEnd, *args)

def timedRepeat(timePeriod, runCondition, taskOnStart, taskOnEnd, *startArgs):
    while runCondition[0]:
        taskOnStart(*startArgs)
        sleep(timePeriod)
    
    taskOnEnd()
