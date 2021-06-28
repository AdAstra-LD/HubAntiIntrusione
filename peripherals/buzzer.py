import pwm 
import threading

class Buzzer:
    def __init__(self, pin):
        pinMode(pin, OUTPUT)
        self.pin = pin
        self.continueFlag = threading.Event()
        self.continueFlag.set()
        self.running = False
    
    def _body(self, enableConditionMO, initialFreq, finalFreq, increment, delay):
        if initialFreq == 0 or initialFreq < finalFreq or delay == 0 or increment == 0:
            return
        
        self.running = True
        
        #enableConditionMO.set(True)
        currentFreq = initialFreq
        
        while enableConditionMO.get():
            if not self.continueFlag.is_set():
                pwm.write(self.pin, 0, 0)
                
            self.continueFlag.wait()
            #we are using MICROS so every sec is 1000000 of micros. 
            #// is the int division, pwm.write period doesn't accept floats
            period=1000000//currentFreq
            
            #set the period of the buzzer and the duty to 50% of the period
            pwm.write(self.pin, period, period//2, MICROS)
            
            # increment the frequency every loop
            currentFreq = currentFreq + increment 
            
            # reset period
            if abs(currentFreq - finalFreq) < abs(increment):
                currentFreq = initialFreq

            sleep(delay)
        
        print("Stopping buzzer thread...")
        pwm.write(self.pin, 0, 0)
        self.running = False
    
    def play(self, enableConditionMO, initialFreq = 2350, finalFreq = 200, increment = -12, delay = 2):
        enableConditionMO.set(True)
        
        if self.running:
            print("Resuming buzzer thread")
            self.continueFlag.set()
        else:
            print("Starting buzzer thread")
            thread(self._body, enableConditionMO, initialFreq, finalFreq, increment, delay)