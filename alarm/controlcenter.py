import threading

import mutableObject as mo
import glob
#from smartsensors import digitalSensors as ds

class ControlCenter():
    def __init__(self, lcd, ledRGB, buzzer, enableButton, IRsensor):
        self.enable = { 
            #Global Vars for the alarm
            "dashboard" : mo.Mutable(True),
            "audio" : mo.Mutable(True),
            "flash" : mo.Mutable(True),
            "alarm" : mo.Mutable(False),
            "mqttSend" : mo.Mutable(False),
        }
        
        self.running = { 
            #Global Vars for system processes
            "wifi" : mo.Mutable(False),
            "mqtt" : mo.Mutable(False),
            "alarm" : mo.Mutable(False),
            "mqttSend" : mo.Mutable(False),
        }
        
        self.dashboard = None
        
        self.lcd = lcd
        self.ledRGB = ledRGB
        self.buzzer = buzzer
        
        #PINS MUST BE ALREADY INITIALIZED, BEFORE THESE INTERRUPTS ARE SET UP
        onPinFall(enableButton, self.toggleOnOff, debounce=100)
        onPinRise(IRsensor, self.intrusione, debounce = 500)
        onPinFall(IRsensor, self.stopAlarm, debounce = 500)

    def toggleOnOff(self):
        isAlarmOn = self.enable["alarm"].get()
        
        if isAlarmOn: #se è inizialmente attivo
            self.ledRGB.memorizeColor(0, 0, 0)
            self.ledRGB.RGBoff()
            self.stopAlarm()
            print("Sistema disabilitato") #viene disattivato
        else:
            self.ledRGB.RGBset(0, 0, 1)
            print("Sistema abilitato")
        
        self.enable["alarm"].set(not isAlarmOn)
        
        self.dashboard.displayStatus()
            
        
    def intrusione(self):
        self.dashboard.continueFlag.clear()
        if (self.enable["alarm"].get() == True):
            self.running["alarm"].set(True)
            print("Intrusione!!!")
            self.ledRGB.flash(self.enable["flash"], flashFrequency = 20, colorTuple = (1, 0, 0))
            #self.buzzer.play(self.enable["audio"])
            self.lcd.lock.acquire()
            self.lcd.printLine("!  Intruder  !", 1, align = "CENTER")
        else:
            print("Movimento rilevato... ma l'allarme non e' inserito")
            self.lcd.lock.acquire()
            self.lcd.printLine("Alarm busy...", 1, align = "CENTER")
        
        self.lcd.lock.release()
        print("lock released")
    
    def stopAlarm(self):
        if self.running["alarm"].get():
            self.buzzer.continueFlag.clear()
            self.ledRGB.continueFlag.clear()
            self.lcd.lock.acquire()
            self.lcd.clear()
            self.lcd.lock.release()
            print("Alarm signal down...")
        
        self.dashboard.continueFlag.set()
        self.dashboard.displayStatus()