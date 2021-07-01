import threading
import glob

from wireless import wifi
from mqtt import mqtt

# import wifi support
from espressif.esp32net import esp32wifi as wifi_driver
import peripherals.specialChars as chars
import utilities.cString as cString
import utilities.music as music
import alarm.settings as settings

wifi_driver.auto_init()

enableAlarmKey = "enableAlarm"
intruderKey = 'intruder'
intrudersCountKey = 'intrudersCount'

class ControlCenter():
    def __init__(self, systemSettings, alarmDataCenter, lcd, ledRGB, buzzer, enableButton, IRsensor):
        self.settings = systemSettings
        self.button = enableButton
        self.IRsensor = IRsensor
        
        self.intrudersCount = 0
        self.enableAlarm = False
        self.alarmRunning = False
        self.sensorBusy = False
        self.wifiOk = False
        self.MQTTOk = False
        
        self.mqttClient = None
        self.dataCenter = alarmDataCenter
        
        self.lcd = lcd
        self.ledRGB = ledRGB
        self.buzzer = buzzer
        
        #PINS MUST BE ALREADY INITIALIZED, BEFORE THESE INTERRUPTS ARE SET UP
        onPinFall(enableButton, self.toggleOnOff, debounce=100)
        onPinRise(IRsensor, self.intrusione, debounce = 500)
        onPinFall(IRsensor, self.stopAlarm, debounce = 500)

    def linkAndStartComm(self, wifiNetwork, wifiKey, mqttClient, broker, port = 1883, attempts = 5):
        self.lcd.lock.acquire()
        
        for retry in range(attempts):
            try:
                print("linking WiFi")
                self.ledRGB.RGBset(R = 255, G = 255, B = 0)
                self.ledRGB.quickBlink(R = 255, G = 255, B = 0)
                self.lcd.printLine("Attempting WiFi\nconnection. [" + str(retry+1) + "]", clearPrevious = True)
                wifi.link(wifiNetwork, wifi.WIFI_WPA2, wifiKey)
                print("WiFi ok")
                break
            except Exception as e:
                print("WiFi error: ", e)
                if (retry == attempts-1):
                    
                    print("Too many errors.")
                    self.lcd.writeCGRAM(chars.SAD_FACE, 7) #Temp buffer --> #SAD
                    self.buzzer.playSequence(music.failureTone, BPM = 140)
                    self.ledRGB.RGBset(R = 255, G = 0, B = 0)
                    self.lcd.printLine("WiFi connection\nfailed. "  + self.lcd.CGRAM[7] + "\nProceeding w/o\nconnectivity.", sentenceDelay = 1500, clearPrevious = True)
                    sleep(2000)
                    self.lcd.clear()
                    self.lcd.lock.release()
                    return
                sleep(500)
        
        self.wifiOk = True
        self.ledRGB.RGBset(R = 0, G = 255, B = 0)
        sleep(200)
        #try:
        for retry in range(attempts):
            try:
                print("connecting with broker")
                self.ledRGB.RGBset(R = 255, G = 255, B = 0)
                self.ledRGB.quickBlink(R = 255, G = 255, B = 0)
                self.lcd.printLine("Attempting MQTT\nconnection. [" + str(retry+1) + "]", clearPrevious = True)
                mqttClient.connect(broker, port, keepalive = 30)
                #self.mqttClient.connect("192.168.1.67", port=1886, keepalive = 30)
                print("Connected broker")
                break
            except Exception as e:
                print("MQTT error: " + str(e))
                
                if retry == attempts-1:
                    print("Too many errors.")
                    self.lcd.writeCGRAM(chars.SAD_FACE, 7) #Temp buffer --> #SAD
                    self.buzzer.playSequence(music.failureTone, BPM = 140)
                    self.ledRGB.RGBset(R = 255, G = 0, B = 0)
                    self.lcd.printLine("MQTT connection\nfailed. "  + self.lcd.CGRAM[7] + "\nProceeding w/o\nconnectivity.", clearPrevious = True)
                    sleep(2000)
                    self.lcd.clear()
                    self.lcd.lock.release()
                    return
                sleep(500)
                
        self.lcd.lock.release()
        
        self.MQTTOk = True
        mqttClient.set_will(glob.topicRoot + '/#', str("Error"), 2, True)
        mqttClient.loop()
        self.mqttClient = mqttClient
        
        self.ledRGB.RGBset(R = 0, G = 255, B = 0)
        sleep(200)
        
        self.dataCenter.enableDataSend = True
        mqttClient.publish(str(glob.topicRoot + '/' + enableAlarmKey), str(self.enableAlarm), 2, retain = True)
        mqttClient.publish(str(glob.topicRoot + '/' + intruderKey), "No activity", 2)
        mqttClient.publish(str(glob.topicRoot + '/' + intrudersCountKey), str(self.intrudersCount), 2, retain = True)

    def toggleOnOff(self):
        if self.settings.systemStatus == settings.SYSTEM_PROTECTED:
            self.dataCenter.continueFlag.clear()
            self.lcd.lock.acquire()
            self.lcd.printLine("Enter password:", align = "CENTER")
            sleep(1000)
            self.lcd.lock.release()
            if not self.settings.passwordScreen(toCompare = self.settings.pw, discardable = True): #wrong password or discarded
                return
        
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
            self.mqttClient.publish(str(glob.topicRoot + '/' + enableAlarmKey), str(self.enableAlarm), 2, retain = True)
        
        self.dataCenter.continueFlag.set()
        self.displayStatus()
            
        
    def intrusione(self):
        self.dataCenter.continueFlag.clear()
        self.sensorBusy = True
        self.lcd.lock.acquire()
        if self.enableAlarm:
            self.alarmRunning = True
            print("Intrusione!!!")
            self.intrudersCount += 1
            
            if self.mqttClient is not None:
                self.mqttClient.publish(str(glob.topicRoot + '/' + intrudersCountKey), str(self.intrudersCount), 2, retain = True)
                self.mqttClient.publish(str(glob.topicRoot + '/' + intruderKey), "Intruder!", 2, retain = True)
                
            self.buzzer.soundAlarm()
            self.ledRGB.flash(flashFrequency = 20, colorTuple = (255, 0, 0))
            self.lcd.printLine("!  Intruder  !", 1, align = "CENTER")
        else:
            print("Movimento rilevato... [allarme non inserito]")
            
            if self.mqttClient is not None:
                self.mqttClient.publish(str(glob.topicRoot + '/' + intruderKey), "Sensor busy", 2)
                
            self.lcd.printLine("Alarm busy...", 1, align = "CENTER")
        
        self.lcd.lock.release()
        #print("lcd lock released")
    
    def checkBusy(self):
        if digitalRead(self.IRsensor) == HIGH:
            self.sensorBusy = True
            self.dataCenter.continueFlag.clear()
            self.lcd.lock.acquire()
            
            if self.mqttClient is not None:
                self.mqttClient.publish(str(glob.topicRoot + '/' + intruderKey), "Sensor busy", 2)
            
            self.lcd.printLine("Alarm busy...", 1, align = "CENTER")
            self.lcd.lock.release()
        else:
            self.sensorBusy = False
            
            if self.mqttClient is not None:
                self.mqttClient.publish(str(glob.topicRoot + '/' + intruderKey), "No activity", 2)
            
            self.dataCenter.continueFlag.set()
            self.displayStatus()
    
    def stopAlarm(self):
        if self.alarmRunning:
            self.buzzer.continueFlag.clear()
            self.ledRGB.continueFlag.clear()
            self.lcd.lock.acquire()
            self.lcd.clear()
            self.lcd.lock.release()
            print("Alarm signal down...")
        
        self.checkBusy()
        self.alarmRunning = False

    def displayStatus(self):
        if self.sensorBusy:
            return
        
        string = ""
        
        #if self.controlCenter.enableAlarm:
        #    string += self.lcd.CGRAM[4]  #EXCLAMATION
        
        if self.MQTTOk:
            string += self.lcd.CGRAM[7] #MQTT Logo
        
        string += self.lcd.CGRAM[6]
        
        self.lcd.lock.acquire()
        self.lcd.writeCGRAM(chars.MQTT, 7) #this acts as a temp buffer
        
        if self.wifiOk:
            self.lcd.writeCGRAM(chars.WIFI, 6)
        else:
            self.lcd.writeCGRAM(chars.NO_SIGNAL, 6) 
        
        self.lcd.print(cString.lpad(string, 8), row = 0, align='RIGHT', delay = 0)
        self.lcd.lock.release()