import glob

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
        ledColorlow = ledColor.lower()
        
        if ledColorlow == 'r':
            return self.pinTuple[0]
        elif ledColorlow == 'g':
            return self.pinTuple[1]
        elif ledColorlow == 'b':
            return self.pinTuple[2]
        
        return None

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
        self.memorizeCurrentColor()
        self.RGBoff()
        
        glob.flashPin(self.ledColorToPin(color), flashFrequency)
        self.restoreColor()