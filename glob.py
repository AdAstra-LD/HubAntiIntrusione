#Global Vars
alarmEnable = False;
audioEnable = True;
flashEnable = True;

#Global Vars for tasks
enable_readAmbientLight = True
enable_readTemperature = True
enable_readHumidity = True

#Peripherals
lcd = None
pad = None
pinTuple = None

#Utilities
def isNumber(s):
    if s == None:
        return False
        
    try:
        int(s)
        return True
    except ValueError:
        return False

def setupRGBled (R, G, B):
    pinMode(R, OUTPUT)
    pinMode(G, OUTPUT)
    pinMode(B, OUTPUT)
    
    print("LED pins are set up: " + str(R) + ", " + str(G) + ", " + str(B))
    
    global pinTuple
    pinTuple = (R, G, B)
