import threading
import glob

from wireless import wifi
from mqtt import mqtt

# import wifi support
from espressif.esp32net import esp32wifi as wifi_driver
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
        
        self.enableAlarm = False
        self.alarmRunning = False
        self.controlBusy = False
        self.sensorBusy = False
        self.wifiOk = False
        self.MQTTOk = False
        
        self.mqttLock = None
        self.mqttClient = None
        self.dataCenter = alarmDataCenter
        self.intrudersCount = 0
        
        self.lcd = lcd
        self.ledRGB = ledRGB
        self.buzzer = buzzer
    
    def enableIO(self):
        #PINS MUST BE ALREADY INITIALIZED, BEFORE THESE INTERRUPTS ARE SET UP
        onPinFall(self.button, self.toggleOnOff, debounce= 70)
        onPinRise(self.IRsensor, self.alarmHigh, debounce = 75)
        onPinFall(self.IRsensor, self.stopAlarm, debounce = 500)

    def linkAndStartComm(self, wifiNetwork, wifiKey, mqttClient, mqttLock, broker, port = 1883, attempts = 5):
        self.lcd.lock.acquire()
        
        for retry in range(attempts):
            try:
                print("linking WiFi")
                self.ledRGB.RGBset(R = 255, G = 255, B = 0)
                self.ledRGB.quickBlink(R = 255, G = 255, B = 0)
                self.lcd.printLine("Attempting WiFi\nlink. [" + str(retry+1) + "]")
                wifi.link(wifiNetwork, wifi.WIFI_WPA2, wifiKey)
                print("WiFi ok")
                break
            except Exception as e:
                print("WiFi error: ", e)
                if (retry == attempts-1):
                    
                    print("WiFi errors.")
                    self.buzzer.playSequence(music.failureTone, BPM = 140)
                    self.ledRGB.RGBset(R = 255, G = 0, B = 0)
                    self.lcd.printLine("WiFi link\nfailed. "  + self.lcd.CGRAM[7] + "\nProceeding w/o\nconnectivity.", sentenceDelay = 1500)
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
                print("linking broker")
                self.ledRGB.RGBset(R = 255, G = 255, B = 0)
                self.ledRGB.quickBlink(R = 255, G = 255, B = 0)
                self.lcd.printLine("Attempting MQTT\nlink. [" + str(retry+1) + "]")
                mqttClient.connect(broker, port, keepalive = 30)
                #self.mqttClient.connect("192.168.1.67", port=1886, keepalive = 30)
                print("OK broker")
                break
            except Exception as e:
                print("MQTT error: " + str(e))
                
                if retry == attempts-1:
                    print("MQTT errors")
                    self.buzzer.playSequence(music.failureTone, BPM = 140)
                    self.ledRGB.RGBset(R = 255, G = 0, B = 0)
                    self.lcd.printLine("MQTT link\nfailed. "  + self.lcd.CGRAM[7] + "\nProceeding w/o\nconnectivity.")
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
        self.mqttLock = mqttLock
        
        self.ledRGB.RGBset(R = 0, G = 255, B = 0)
        sleep(50)
        
        self.dataCenter.enableDataSend = True
        self.mqttLock.acquire()
        self.mqttClient.publish(str(glob.topicRoot + '/' + enableAlarmKey), str(self.enableAlarm), 2, retain = True)
        self.mqttClient.publish(str(glob.topicRoot + '/' + intruderKey), "No activity", 2)
        self.mqttClient.publish(str(glob.topicRoot + '/' + intrudersCountKey), str(self.intrudersCount), 2, retain = True)
        self.mqttLock.release()
        
    def linkMQTTClient(self, client, lock):
        self.mqttClient = client
        self.mqttLock = lock
        
    def toggleOnOff(self):
        if self.controlBusy:
            return
        
        self.controlBusy = True
        if self.settings.systemStatus == settings.SYSTEM_PROTECTED and not self.alarmRunning:
            self.dataCenter.continueFlag.clear()
            self.lcd.lock.acquire()
            self.lcd.printLine("Enter password:", align = "CENTER")
            sleep(1200)
            self.lcd.lock.release()
            if self.settings.passwordScreen(toCompare = self.settings.pw, discardable = True) == False: #wrong password or discarded
                self.displayStatus()
                self.dataCenter.continueFlag.set()
                return
        
        if self.enableAlarm: #se è inizialmente attivo, esegue azioni di disattivazione
            self.ledRGB.memorizeColor(0, 0, 0)
            self.ledRGB.RGBset(0, 0, 0)
            self.stopAlarm()
            print("Alm ON") #
        else: #diversamente, procede all'attivazione
            self.ledRGB.RGBset(0, 0, 255)
            print("Alm OFF") #
        
        self.enableAlarm = not self.enableAlarm
        
        if self.mqttClient is not None:
            self.mqttClient.publish(str(glob.topicRoot + '/' + enableAlarmKey), str(self.enableAlarm), 2, retain = True)
        
        if not self.checkSensorBusy(showOnDisplay = True):
            self.displayStatus()
            self.dataCenter.continueFlag.set()
            
        self.controlBusy = False
        
    def alarmHigh(self):
        if self.enableAlarm and not self.sensorBusy:
            self.dataCenter.continueFlag.clear()
            self.alarmRunning = True
            self.intrudersCount += 1
            print("alarmHigh!")
            
            if self.mqttClient is not None:
                self.mqttLock.acquire()
                self.mqttClient.publish(str(glob.topicRoot + '/' + intrudersCountKey), str(self.intrudersCount), 2, retain = True)
                self.mqttClient.publish(str(glob.topicRoot + '/' + intruderKey), "Intruder!", 2, retain = False)
                self.mqttLock.release()
            
            sleep(100)
            self.lcd.lock.acquire()
            self.lcd.printLine("!  Intruder  !", row=1, align = "CENTER")
            self.lcd.lock.release()
            self.buzzer.soundAlarm()
            self.ledRGB.flash(flashFrequency = 20, colorTuple = (255, 0, 0))
        else:
            self.sensorSetBusy() #we already know it will be busy
        
    def sensorSetBusy(self, showOnDisplay = False):
        self.sensorBusy = True
            
        if self.mqttClient is not None:
            self.mqttLock.acquire()
            self.mqttClient.publish(str(glob.topicRoot + '/' + intruderKey), "Sensor busy", 2)
            self.mqttLock.release()
        
        print("Alarm busy...")
        if showOnDisplay:
            self.lcd.lock.acquire()
            self.lcd.printLine("Alarm busy...", 1, align = "CENTER", clearPrevious = False)
            self.lcd.lock.release()
        
    def checkSensorBusy(self, showOnDisplay = False):
        if digitalRead(self.IRsensor) == HIGH:
            self.sensorSetBusy(showOnDisplay)
            return True
        else:
            self.sensorBusy = False
            
            if self.mqttClient is not None:
                self.mqttLock.acquire()
                self.mqttClient.publish(str(glob.topicRoot + '/' + intruderKey), "No activity", 2)
                self.mqttLock.release()
                
            self.displayStatus()
            return False
    
    def stopAlarm(self):
        print("Signal down")
        if self.alarmRunning:
            self.buzzer.continueFlag.clear()
            self.ledRGB.continueFlag.clear()
            self.lcd.lock.acquire()
            self.lcd.clear()
            self.lcd.lock.release()
        
        if not self.checkSensorBusy():
            self.dataCenter.continueFlag.set()
        self.alarmRunning = False

    def displayStatus(self):
        string = ""

        if self.MQTTOk:
            string += self.lcd.CGRAM[4] #MQTT Logo
        
        if self.wifiOk:
            string += self.lcd.CGRAM[5] #WIFI icon
        else:
            string += self.lcd.CGRAM[6] #NO SIGNAL icon
        
        self.lcd.lock.acquire()
        self.lcd.print(cString.lpad(string, 8), row = 0, align='RIGHT', delay = 0)
        self.lcd.lock.release()