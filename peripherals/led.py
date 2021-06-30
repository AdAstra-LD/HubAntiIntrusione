import glob
import utilities.cMath as cMath
import threading

colorPinDict = {
    "r" : (0,),
    "g" : (1,),
    "b" : (2,),
    
    "c" : (1, 2),
    "m" : (2, 0),
    "y" : (0, 1),
    
    "w" : (0, 1, 2)
}

class RGBLed:
    def __init__(self, Rpin, Gpin, Bpin):
        self.cur = [0, 0, 0]
        self.mem = [0, 0, 0]
        
        self.continueFlag = threading.Event()
        self.continueFlag.set()
        self.running = False
        
        pinMode(Rpin, OUTPUT)
        pinMode(Gpin, OUTPUT)
        pinMode(Bpin, OUTPUT)
        
        self.pinTuple = (Rpin, Gpin, Bpin)
        self.RGBoff()
        
        print("LEDs are set up: " + str(Rpin) + ", " + str(Gpin) + ", " + str(Bpin))
        
    def ledColorToPins(self, ledColor):
        global colorPinDict
        ledColorlow = ledColor.lower()
        return [self.pinTuple[pos] for pos in colorPinDict[ledColorlow]]
    
    def RGBoff(self):
        digitalWrite(self.pinTuple[0], LOW)
        digitalWrite(self.pinTuple[1], LOW)
        digitalWrite(self.pinTuple[2], LOW)
        
        self.cur = [0, 0, 0]
    
    def RGBset(self, R = None, G = None, B = None, colorTuple = None): 
        if colorTuple == None:
            colorTuple = (R, G, B)
        
        for cIndex in range(3):
            color = colorTuple[cIndex]
            
            if cMath.isNumber(color):
                status = HIGH if(color > 0) else LOW
                digitalWrite(self.pinTuple[cIndex], status)
                self.cur[cIndex] = color
    
    def memorizeColor (self, R = None, G = None, B = None, colorTuple = None):
        if colorTuple == None:
            colorTuple = (R, G, B)
        
        for index in range(3):
            self.mem[index] = colorTuple[index]
    
    def memorizeCurrentColor (self):
        for index in range(3):
            self.mem[index] = self.cur[index]
    
    def restoreColor (self):
        self.RGBset(colorTuple = self.mem)
        
    def _flashTask(self, enableConditionMO, flashFrequency, R = None, G = None, B = None, colorTuple = None):
        self.running = True 
        enableConditionMO.set(True)
        self.memorizeCurrentColor()
        self.RGBoff()
        #pinTuple = self.ledColorToPins(color)
        
        flashFrequency = max(1, flashFrequency)
        period = 1000//flashFrequency
        
        if colorTuple is None:
            colorTuple = (R, G, B)
        
        while enableConditionMO.get():
            if not self.continueFlag.is_set():
                self.restoreColor()
            self.continueFlag.wait()
            self.RGBset(colorTuple = colorTuple)
            sleep(period)
            self.RGBset(0, 0, 0)
            sleep(period)
        
        self.restoreColor()
        self.running = False 
        print("Stopping LED thread")
            
    def flash(self, enableConditionMO, flashFrequency = 20, R = None, G = None, B = None, colorTuple = None):
        enableConditionMO.set(True)
        
        if self.running:
            print("Resuming LED thread")
            self.continueFlag.set()
        else:
            print("Starting LED thread")
            thread(self._flashTask, enableConditionMO, flashFrequency, R, G, B, colorTuple)
        
    def quickBlink(self, R = None, G = None, B = None, colorTuple = None, flashFrequencyHz = 20, times = 3):
        self.memorizeCurrentColor()
        self.RGBoff()
        period = max(1, 1000//flashFrequencyHz)
        
        for x in range(times):
            self.RGBset(R, G, B, colorTuple)
            sleep(period)
            self.RGBoff()
            sleep(period)
        
        self.restoreColor()
        