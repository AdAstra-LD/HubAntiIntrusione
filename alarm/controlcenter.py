import threading

import utilities.mutableObject as mo
import glob

enableAlarmKey = "enableAlarm"
#from smartsensors import digitalSensors as ds

class ControlCenter():
    def __init__(self, alarmDataCenter, alarmCommunicationCenter, lcd, ledRGB, buzzer, enableButton, IRsensor):
        self.enableAlarm = False
        self.alarmRunning = False
        
        self.dataCenter = alarmDataCenter
        self.commCenter = alarmCommunicationCenter
        self.dashboard = None #to be linked later
        
        self.lcd = lcd
        self.ledRGB = ledRGB
        self.buzzer = buzzer
        
        #PINS MUST BE ALREADY INITIALIZED, BEFORE THESE INTERRUPTS ARE SET UP
        onPinFall(enableButton, self.toggleOnOff, debounce=100)
        onPinRise(IRsensor, self.intrusione, debounce = 500)
        onPinFall(IRsensor, self.stopAlarm, debounce = 500)

    def toggleOnOff(self):
        if self.enableAlarm: #se è inizialmente attivo
            self.ledRGB.memorizeColor(0, 0, 0)
            self.ledRGB.RGBoff()
            self.stopAlarm()
            print("Sistema disabilitato") #viene disattivato
        else:
            self.ledRGB.RGBset(0, 0, 1)
            print("Sistema abilitato")
        
        self.enableAlarm = not self.enableAlarm
        self.commCenter.mqttClient.publish(str("roomIOT2021" + '/' + enableAlarmKey), self.enableAlarm, 2)
        
        self.dashboard.displayStatus()
            
        
    def intrusione(self):
        self.dashboard.continueFlag.clear()
        self.dataCenter.continueFlag.clear()
        self.commCenter.continueFlag.clear()
        if self.enableAlarm:
            self.alarmRunning = True
            print("Intrusione!!!")
            self.ledRGB.flash(flashFrequency = 20, colorTuple = (1, 0, 0))
            self.buzzer.play()
            self.lcd.lock.acquire()
            self.lcd.printLine("!  Intruder  !", 1, align = "CENTER")
        else:
            print("Movimento rilevato... ma l'allarme non e' inserito")
            self.lcd.lock.acquire()
            self.lcd.printLine("Alarm busy...", 1, align = "CENTER")
        
        self.lcd.lock.release()
        print("lock released")
    
    def stopAlarm(self):
        if self.alarmRunning:
            self.buzzer.continueFlag.clear()
            self.ledRGB.continueFlag.clear()
            self.lcd.lock.acquire()
            self.lcd.clear()
            self.lcd.lock.release()
            print("Alarm signal down...")
        
        self.dashboard.continueFlag.set()
        self.dataCenter.continueFlag.set()
        self.commCenter.continueFlag.set()