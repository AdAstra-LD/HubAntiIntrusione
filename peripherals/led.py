import glob
import utilities.cMath as cMath
import threading

colorDict = {
    "r" : (255, 0, 0),
    "g" : (0, 255, 0),
    "b" : (0, 0, 255),
    
    "c" : (0, 255, 255),
    "m" : (255, 0, 255),
    "y" : (255, 255, 0),
    
    "w" : (255, 255, 255)
}

class RGBLed:
    def __init__(self, Rpin, Gpin, Bpin):
        self.cur = [0, 0, 0]
        self.mem = [0, 0, 0]
        
        self.mqttClient = None #da linkare in un secondo momento, per eventualmente abilitare la funzionalità di send
        self.topicName = ""
        
        self.enable = True
        self.continueFlag = threading.Event()
        self.continueFlag.set()
        self.running = False
        
        pinMode(Rpin, OUTPUT)
        pinMode(Gpin, OUTPUT)
        pinMode(Bpin, OUTPUT)
        
        self.pinTuple = (Rpin, Gpin, Bpin)
        self.RGBset(0, 0, 0)
        
        print("LEDs are set up: " + str(Rpin) + ", " + str(Gpin) + ", " + str(Bpin))
    
    def linkMQTTClient(self, mqttClient, topicName):
        self.mqttClient = mqttClient
        self.topicName = topicName
    
    def RGBset(self, R = None, G = None, B = None, colorTuple = None, send = True): 
        if colorTuple == None:
            colorTuple = (R, G, B)
        
        for cIndex in range(3):
            color = colorTuple[cIndex]
            
            if cMath.isNumber(color):
                status = HIGH if(color > 0) else LOW
                digitalWrite(self.pinTuple[cIndex], status)
                self.cur[cIndex] = min(color, 255)
        
        if send and self.mqttClient is not None and self.topicName is not None and len(self.topicName) > 0:
            self.mqttClient.publish(self.topicName, str([c for c in self.cur]), 1)
    
    def rainbowFade(self, duration = 1000, times = 1):
        pauseTime = max(1, duration//6)
        self.memorizeCurrentColor()
        
        for x in range(times):
            self.RGBset(R = 255, G = 0, B = 0)
            sleep(pauseTime)
            self.RGBset(R = 255, G = 255, B = 0)
            sleep(pauseTime)
            self.RGBset(R = 0, G = 255, B = 0)
            sleep(pauseTime)
            self.RGBset(R = 0, G = 255, B = 255)
            sleep(pauseTime)
            self.RGBset(R = 0, G = 0, B = 255)
            sleep(pauseTime)
            self.RGBset(R = 255, G = 0, B = 255)
            sleep(pauseTime)
        
        print("restoring color")
        self.restoreColor()
    
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
        
    def _flashTask(self, flashFrequency, R = None, G = None, B = None, colorTuple = None):
        self.running = True 
        self.memorizeCurrentColor()
        self.RGBset(0, 0, 0)
        #pinTuple = self.ledColorToPins(color)
        
        flashFrequency = max(1, flashFrequency)
        period = 1000//flashFrequency
        
        if colorTuple is None:
            colorTuple = (R, G, B)
        
        print(str([c for c in colorTuple]))
        if self.mqttClient is not None:
            self.mqttClient.publish(self.topicName, str([c for c in colorTuple]), 1)
        
        while self.enable:
            if not self.continueFlag.is_set():
                self.restoreColor()
            self.continueFlag.wait()
            self.RGBset(colorTuple = colorTuple, send = False)
            sleep(period)
            self.RGBset(0, 0, 0, send = False)
            sleep(period)
        
        self.restoreColor()
        self.running = False 
        print("Stopping LED thread")
            
    def flash(self, flashFrequency = 20, R = None, G = None, B = None, colorTuple = None):
        self.enable = True
        
        if self.running:
            print("Resuming LED thread")
            self.continueFlag.set()
        else:
            print("Starting LED thread")
            thread(self._flashTask, flashFrequency, R, G, B, colorTuple)
        
    def quickBlink(self, R = None, G = None, B = None, colorTuple = None, flashFrequencyHz = 20, times = 3):
        self.memorizeCurrentColor()
        self.RGBset(0, 0, 0)
        period = max(1, 1000//flashFrequencyHz)
        
        for x in range(times):
            self.RGBset(R, G, B, colorTuple)
            sleep(period)
            self.RGBset(0, 0, 0)
            sleep(period)
        
        self.restoreColor()
        