import pwm 
import threading
import glob

class Buzzer:
    def __init__(self, pin):
        pinMode(pin, OUTPUT)
        self.pin = pin
        self.currentFreq = 0

    def loopSound(self, initialFreq, finalFreq, increment, delay):
        #we are using MICROS so every sec is 1000000 of micros. 
        #// is the int division, pwm.write period doesn't accept floats
        period=1000000//self.currentFreq
        
        #set the period of the buzzer and the duty to 50% of the period
        pwm.write(self.pin, period, period//2, MICROS)
        
        # increment the frequency every loop
        self.currentFreq = self.currentFreq + increment 
        
        # reset period
        if abs(self.currentFreq - finalFreq) < abs(increment):
            self.currentFreq = initialFreq
            print("ping")
                
    def play(self, initialFreq = 2350, finalFreq = 200, increment = -12, delay = 2):
        if initialFreq == 0 or initialFreq < finalFreq or delay == 0 or increment == 0:
            return
        
        glob.enable["audio"].set(True)
        
        self.currentFreq = initialFreq
        thread(glob.timedRepeat, delay, glob.enable["audio"], 
            [self.loopSound], [[initialFreq, finalFreq, increment, delay]], #funzioni di start
            [pwm.write], [[self.pin, 0, 0]]) #funzioni finali