import glob

def flash(ledPin, flashFrequency):
    glob.flashEnable = True
    thread(__flashTask, ledPin, flashFrequency)
    
def RGBoff(pinTuple = glob.pinTuple):
    digitalWrite(pinTuple[0], LOW)
    digitalWrite(pinTuple[1], LOW)
    digitalWrite(pinTuple[2], LOW)
    
def RGBset(R, G, B, pinTuple = glob.pinTuple): 
    colorTuple = (R, G, B)
    
    for cIndex in range(3):
        color = colorTuple[cIndex]
        
        if glob.isNumber(color):
            status = HIGH if(color > 0) else LOW
            digitalWrite(pinTuple[cIndex], status)
            
def __flashTask (ledPin, flashFrequency):    
    if (flashFrequency == 0):
        flashFrequency = 1
    
    RGBoff()
    while (glob.flashEnable):
        pinToggle(ledPin)
        sleep(1000//flashFrequency)
    