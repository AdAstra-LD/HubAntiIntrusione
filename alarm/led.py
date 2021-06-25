import glob
import threading

colorPinDict = {
    "r" : 0,
    "g" : 1,
    "b" : 2,
    
    "c" : (1, 2),
    "m" : (2, 0),
    "y" : (0, 1),
    
    "w" : (0, 1, 2)
}

class RGBLed:
    def __init__(self, Rpin, Gpin, Bpin):
        pinMode(Rpin, OUTPUT)
        pinMode(Gpin, OUTPUT)
        pinMode(Bpin, OUTPUT)
        
        print("LED pins are set up: " + str(Rpin) + ", " + str(Gpin) + ", " + str(Bpin))
        
        self.cur = [0, 0, 0]
        self.mem = [0, 0, 0]
        self.pinTuple = (Rpin, Gpin, Bpin)
        
    def ledColorToPin(self, ledColor):
        global colorPinDict
        ledColorlow = ledColor.lower()
        
        return colorPinDict[ledColor]

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
            
            if glob.isNumber(color):
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
    
    def flash(self, flashFrequency = 20, color = 'R'):
        glob.enable["flash"].set(True)
        self.memorizeCurrentColor()
        self.RGBoff()
        
        pin = self.ledColorToPin(color)

        glob.flashPins(flashFrequency, glob.enable["flash"], pin, [self.restoreColor])
    
    def threadedBlink(self, R = None, G = None, B = None, colorTuple = None, times = 5):
        thread(self.quickBlink, R, G, B, colorTuple, times)
        
    def quickBlink(self, R = None, G = None, B = None, colorTuple = None, times = 2):
        self.memorizeCurrentColor()
        self.RGBoff()
        
        flashFrequency = 20 #Hz
        period = 1000//flashFrequency
        for x in range(times):
            self.RGBset(R, G, B, colorTuple)
            sleep(time)
            self.RGBoff()
            sleep(time)
        
        self.restoreColor()
        