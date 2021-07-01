import pwm 
import threading
import utilities.cMath as cMath
import utilities.music as music

class Buzzer:
    def __init__(self, pin):
        pinMode(pin, OUTPUT)
        self.pin = pin
        
        self.mqttClient = None
        self.topicName = ""
        
        self.enable = True
        self.playing = False
        
        self.lock = threading.Lock()
        self.continueFlag = threading.Event()
        self.continueFlag.set()
    
    def linkMQTTClient(self, mqttClient, topicName = "roomIOT2021/buzzer"):
        self.mqttClient = mqttClient
        self.topicName = topicName
    
    def sendStatus(self):
        if self.mqttClient is not None and self.topicName is not None and len(self.topicName) > 0:
            self.mqttClient.publish(self.topicName, str(self.playing), 1)
    
    def playTone(self, fixedfrequency, duration = 50,  duty = 50):
        duty = min(duty, 100)
        period=max(1, 1000000//fixedfrequency)
            
        self.lock.acquire()
        
        pwm.write(self.pin, period, (period*duty)//100, MICROS)
        sleep(max(1, duration))
        pwm.write(self.pin, 0, 0)
        
        self.lock.release()
        
    def playNote(self, note, duration, octaveModifier = 0, BPM = 120, duty = 50):

        duty = min(duty, 100)
        freq = music.notes[note]*cMath.exp(2, octaveModifier)
        period=max(1, round(1000000//freq))
            
        self.lock.acquire()
        
        pwm.write(self.pin, period, (period*duty)//100, MICROS)
        sleep(max(1, round(1000*60*4*duration/BPM) ))
        pwm.write(self.pin, 0, 0)
        
        self.lock.release()
    
    def playSequence(self, sequence, BPM = 120, duty = 50, send = True):

        duty = min(duty, 100)
        self.lock.acquire()
        
        if send:
            self.sendStatus()
        
        print(sequence)
        for x in sequence:
            if x[0] == "P":
                pwm.write(self.pin, 0, 0)
                sleep(max(1, round(1000*60*4*x[1]/BPM) ))
            else:
                freq = music.notes[x[0]]*cMath.exp(2, x[1])
                #print(str(freq))
                period=max(1, round(1000000//freq))
                #print(str(period))
                pwm.write(self.pin, period, (period*duty)//100, MICROS)
                sleep(max(1, round(1000*60*4*x[2]/BPM) ))
        
        pwm.write(self.pin, 0, 0)
        
        if send:
            self.sendStatus()
            
        self.lock.release()
        
    
    def soundAlarm(self, initialFreq = 2350, finalFreq = 200, increment = -12, delay = 2):
        self.enable = True
        
        if self.playing:
            print("Resuming buzzer thread")
            self.continueFlag.set()
        else:
            print("Starting buzzer thread")
            thread(self._bodyAlarm, initialFreq, finalFreq, increment, delay)
    
    def _bodyAlarm(self, initialFreq, finalFreq, increment, delay):
        if initialFreq == 0 or initialFreq < finalFreq or delay == 0 or increment == 0:
            return
        
        self.playing = True
        currentFreq = initialFreq
        
        self.lock.acquire()
        while self.enable:
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
        self.lock.release()
        self.playing = False