import threading
import glob

from wireless import wifi
from mqtt import mqtt

# import wifi support
from espressif.esp32net import esp32wifi as wifi_driver
import peripherals.specialChars as chars
import utilities.cString as cString

wifi_driver.auto_init()

enableAlarmKey = "enableAlarm"

class ControlCenter():
    def __init__(self, alarmDataCenter, mqttClient, lcd, ledRGB, buzzer, enableButton, IRsensor):
        self.intrudersCount = 0
        self.enableAlarm = False
        self.alarmRunning = False
        self.wifiOK = False
        self.MQTTOk = False
        
        self.mqttClient = mqttClient
        self.dataCenter = alarmDataCenter
        
        self.lcd = lcd
        self.ledRGB = ledRGB
        self.buzzer = buzzer
        
        #PINS MUST BE ALREADY INITIALIZED, BEFORE THESE INTERRUPTS ARE SET UP
        onPinFall(enableButton, self.toggleOnOff, debounce=100)
        onPinRise(IRsensor, self.intrusione, debounce = 500)
        onPinFall(IRsensor, self.stopAlarm, debounce = 500)

    def startComm(self, wifiNetwork, wifiKey, broker, port = 1883, attempts = 5):
        for retry in range(attempts):
            try:
                print("Attempting WiFi link...")
                wifi.link(wifiNetwork, wifi.WIFI_WPA2, wifiKey)
                print("WiFi connection successful.")
                break
            except Exception as e:
                print("WiFi connection error: ", e)
                if (retry == attempts-1):
                    self.lcd.lock.acquire()
                    print("Too many errors. Not gonna try anymore.")
                    self.lcd.clear()
                    self.lcd.writeCGRAM(chars.SAD_FACE, 7) #Temp buffer --> #SAD
                    self.lcd.printLine("WiFi connection\nfailed. " + self.lcd.CGRAM[7])
                    sleep(4000)
                    self.lcd.clear()
                    self.lcd.lock.release()
                    return
                sleep(500)
        
        self.wifiOK = True
        
        #try:
        for retry in range(attempts):
            try:
                print("Attempting connection with broker")
                self.mqttClient.connect(broker, port, keepalive = 30)
                #self.mqttClient.connect("192.168.1.67", port=1886, keepalive = 30)
                print("Connected with broker")
                break
            except Exception as e:
                print("MQTT connection error: " + str(e))
                
                if retry == attempts-1:
                    self.lcd.lock.acquire()
                    print("Too many errors. Not gonna try anymore.")
                    self.lcd.clear()
                    self.lcd.writeCGRAM(chars.SAD_FACE, 7) #Temp buffer --> #SAD
                    self.lcd.printLine("MQTT connection\nfailed. " + self.lcd.CGRAM[7])
                    sleep(4000)
                    self.lcd.clear()
                    self.lcd.lock.release()
                    return
                sleep(500)
        
        self.mqttClient.set_will('roomIOT2021/#', str("Error"), 2, True)
        self.mqttClient.loop()
        self.MQTTOk = True
        
        self.dataCenter.enableDataSend = True
        self.mqttClient.publish(str("roomIOT2021" + '/' + enableAlarmKey), str(self.enableAlarm), 2, retain = True)
        self.mqttClient.publish(str("roomIOT2021" + '/' + 'intruder'), "No activity", 2)
        self.mqttClient.publish(str("roomIOT2021" + '/' + 'intrudersCount'), str(self.intrudersCount), 2, retain = True)

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
        
        if self.mqttClient is not None:
            self.mqttClient.publish(str("roomIOT2021" + '/' + enableAlarmKey), str(self.enableAlarm), 2, retain = True)
        
        self.displayStatus()
            
        
    def intrusione(self):
        self.dataCenter.continueFlag.clear()
        self.lcd.lock.acquire()
        if self.enableAlarm:
            self.alarmRunning = True
            print("Intrusione!!!")
            self.intrudersCount += 1
            self.mqttClient.publish(str("roomIOT2021" + '/' + 'intrudersCount'), str(self.intrudersCount), 2, retain = True)
            self.mqttClient.publish(str("roomIOT2021" + '/' + 'intruder'), "Intruder!", 2, retain = True)
            self.buzzer.soundAlarm()
            self.ledRGB.flash(flashFrequency = 20, colorTuple = (255, 0, 0))
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
            self.mqttClient.publish(str("roomIOT2021" + '/' + 'intruder'), "No activity", 2)
            print("Alarm signal down...")
        
        self.dataCenter.continueFlag.set()
        self.alarmRunning = False
        self.displayStatus()
    
    def displayStatus(self):
        string = ""
        
        #if self.controlCenter.enableAlarm:
        #    string += self.lcd.CGRAM[4]  #EXCLAMATION
        
        if self.MQTTOk:
            string += self.lcd.CGRAM[7] #MQTT Logo
        
        string += self.lcd.CGRAM[6]
        
        self.lcd.lock.acquire()
        self.lcd.writeCGRAM(chars.MQTT, 7) #this acts as a temp buffer
        
        if self.wifiOK:
            self.lcd.writeCGRAM(chars.WIFI, 6)
        else:
            self.lcd.writeCGRAM(chars.NO_SIGNAL, 6) 
        
        self.lcd.print(cString.lpad(string, 8), row = 0, align='RIGHT', delay = 0)
        self.lcd.lock.release()