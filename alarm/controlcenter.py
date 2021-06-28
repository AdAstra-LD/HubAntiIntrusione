import threading

import mutableObject as mo
import glob

class ControlCenter():
    def __init__(self, lcd, ledRGB, buzzer, enableButton, IRsensor):
        self.enable = { 
            #Global Vars for system 
            "general" : mo.Mutable(False),
            "audio" : mo.Mutable(False),
            "flash" : mo.Mutable(False),
        }

        self.runDashboard = threading.Event()
        self.runDashboard.set()
        
        self.lcd = lcd
        self.ledRGB = ledRGB
        self.buzzer = buzzer
        
        #PINS MUST BE ALREADY INITIALIZED, BEFORE THESE INTERRUPTS ARE SET UP
        onPinFall(enableButton, self.toggleOnOff)
        onPinRise(IRsensor, self.intrusione)
        onPinFall(IRsensor, self.stopAlarm)

    def toggleOnOff(self):
        status = self.enable["general"].get()
        
        self.enable["general"].set(not status)
        self.enable["audio"].set(not status)
        self.enable["flash"].set(not status)
        
        if (self.enable["general"].get() == True):
            self.ledRGB.RGBset(0, 0, 1)
            print("Sistema abilitato")
            self.lcd.lock.acquire()
            self.lcd.printAtPos(self.lcd.CGRAM[4], self.lcd.nCols-1, 0) #EXCLAMATION
        else:
            self.ledRGB.memorizeColor(0, 0, 0)
            self.stopAlarm()
            self.ledRGB.RGBoff()
            
            self.lcd.lock.acquire()
            self.lcd.printAtPos(' ', self.lcd.nCols-1, 0)
            print("Sistema disabilitato")
        
        self.lcd.lock.release()
            
        
    def intrusione(self):
        if (self.enable["general"].get() == True):
            self.runDashboard.clear()
            self.ledRGB.flash(self.enable["flash"], flashFrequency = 20, color = 'R')
            self.buzzer.play(self.enable["audio"])
            print("Intrusione!!!")
            self.lcd.lock.acquire()
            self.lcd.printLine("!  Intruder  !", 1, align = "CENTER")
        else:
            print("Movimento rilevato... ma l'allarme non e' inserito")
            self.lcd.lock.acquire()
            self.lcd.printLine("Alarm busy...", 1, align = "CENTER")
        
        self.lcd.lock.release()
        print("lock released")
    
    def stopAlarm(self):
        self.enable["audio"].set(False)
        self.enable["flash"].set(False)
        
        print("Alarm signal down...")
        self.runDashboard.set()