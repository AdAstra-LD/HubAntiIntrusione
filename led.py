import glob

cur = [0, 0, 0]
mem = [0, 0, 0]

def RGBoff(pinTuple = None):
    if (pinTuple == None):
        pinTuple = glob.pinTuple
        
    digitalWrite(pinTuple[0], LOW)
    digitalWrite(pinTuple[1], LOW)
    digitalWrite(pinTuple[2], LOW)
    
    cur = [0, 0, 0]
    
def RGBset(R = None, G = None, B = None, colorTuple = None, pinTuple = None): 
    global cur
    
    if colorTuple == None:
        colorTuple = (R, G, B)
    
    if (pinTuple == None):
        pinTuple = glob.pinTuple
    
    for cIndex in range(3):
        color = colorTuple[cIndex]
        
        if glob.isNumber(color):
            status = HIGH if(color > 0) else LOW
            digitalWrite(pinTuple[cIndex], status)
            cur[cIndex] = color

def memorizeColor (R = None, G = None, B = None, colorTuple = None):
    global mem
    
    if colorTuple == None:
        colorTuple = (R, G, B)
    
    for index in range(3):
        mem[index] = colorTuple[index]
    
def memorizeCurrentColor ():
    global mem
    global cur
    
    for index in range(3):
        mem[index] = cur[index]

def restoreColor (pinTuple = None):
    global mem 
    
    RGBset(colorTuple = mem, pinTuple = pinTuple)

def flash(ledPin, flashFrequency):
    glob.flashEnable = True
    thread(__flashTask, ledPin, flashFrequency)

def __flashTask (ledPin, flashFrequency):    
    if (flashFrequency == 0):
        flashFrequency = 1
    
    memorizeCurrentColor()
    RGBoff()
    while (glob.flashEnable):
        pinToggle(ledPin)
        sleep(1000//flashFrequency)
        
    restoreColor()
