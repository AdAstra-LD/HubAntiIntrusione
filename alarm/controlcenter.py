import threading
import glob

enableAlarmKey = "enableAlarm"

class ControlCenter():
    def __init__(self, alarmDataCenter, alarmCommunicationCenter, lcd, ledRGB, buzzer, enableButton, IRsensor):
        self.enableAlarm = False
        self.alarmRunning = False
        
        self.dataCenter = alarmDataCenter
        self.commCenter = alarmCommunicationCenter
        self.commCenter.mqttClient.publish(str("roomIOT2021" + '/' + enableAlarmKey), str(self.enableAlarm), 2)
        
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
            self.ledRGB.RGBset(0, 0, 0)
            self.stopAlarm()
            print("Sistema disabilitato") #viene disattivato
        else:
            self.ledRGB.RGBset(0, 0, 255)
            print("Sistema abilitato")
        
        self.enableAlarm = not self.enableAlarm
        self.commCenter.mqttClient.publish(str("roomIOT2021" + '/' + enableAlarmKey), str(self.enableAlarm), 2)
        
        self.dataCenter.displayStatus()
            
        
    def intrusione(self):
        self.dataCenter.continueFlag.clear()
        self.lcd.lock.acquire()
        if self.enableAlarm:
            self.alarmRunning = True
            print("Intrusione!!!")
            self.ledRGB.flash(flashFrequency = 20, colorTuple = (255, 0, 0))
            self.buzzer.play()
            self.lcd.printLine("!  Intruder  !", 1, align = "CENTER")
        else:
            print("Movimento rilevato... ma l'allarme non e' inserito")
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
        
        self.dataCenter.continueFlag.set()
        self.alarmRunning = False