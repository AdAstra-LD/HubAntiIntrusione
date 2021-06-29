from wireless import wifi
from mqtt import mqtt

# import wifi support
from espressif.esp32net import esp32wifi as wifi_driver
import threading
import mutableObject as mo
import peripherals.specialChars as chars
import glob

wifi_driver.auto_init()

class AlarmComm():
    def __init__(self, alarmControlCenter, alarmDataCenter, networkName, password, attempts = 5, preferredQoS = 2):
        self.controlCenter = alarmControlCenter
        self.dataCenter = alarmDataCenter
        self.continueFlag = threading.Event()
        self.continueFlag.set()
        self.sending = False
        
        self.changeQoS(preferredQoS)
        
        for retry in range(attempts):
            try:
                print("Attempting WiFi link...")
                wifi.link(networkName, wifi.WIFI_WPA2, password)
                print("WiFi connection successful.")
                break
            except Exception as e:
                print("WiFi connection error: ", e)
                if (retry == attempts-1):
                    glob.lcd.lock.acquire()
                    print("Too many errors. Not gonna try anymore.")
                    glob.lcd.clear()
                    glob.lcd.writeCGRAM(chars.SAD_FACE, 7) #Temp buffer --> #SAD
                    glob.lcd.printLine("WiFi connection\nfailed. " + glob.lcd.CGRAM[7])
                    sleep(4000)
                    glob.lcd.clear()
                    glob.lcd.lock.release()
                    self.controlCenter.dashboard.displayStatus()
                    return
                sleep(500)
        
        self.controlCenter.running["wifi"].set(True)
        
        #try:
        self.mqttclient = mqtt.Client("Test", clean_session = True)
        for retry in range(attempts):
            try:
                print("Attempting connection with MQTT broker...")
                self.mqttclient.connect("192.168.1.67", port=1886, keepalive = 20)
                print("MQTT connection successful.")
                break
            except Exception as e:
                print("MQTT connection error: ", e)
                
                if (retry == attempts-1):
                    glob.lcd.lock.acquire()
                    print("Too many errors. Not gonna try anymore.")
                    glob.lcd.clear()
                    glob.lcd.writeCGRAM(chars.SAD_FACE, 7) #Temp buffer --> #SAD
                    glob.lcd.printLine("MQTT connection\nfailed. " + glob.lcd.CGRAM[7])
                    sleep(4000)
                    glob.lcd.clear()
                    glob.lcd.lock.release()
                    self.controlCenter.dashboard.displayStatus()
                    return
                sleep(500)
        
        self.controlCenter.running["mqtt"].set(True)
        self.controlCenter.dashboard.displayStatus()
        #except Exception as e:
        #    sleep(150)
        
    def changeQoS(self, newQoS):
        self.preferredQoS = mo.Mutable(newQoS) if type(newQoS) < PFLOAT else newQoS
        #wrap object if the type is simple [int, smallint...] otherwise keep as-is
    
    def dataSendLoop(self, enableConditionMO, period):
        enableConditionMO.set(True)
        
        if self.sending:
            print("Resuming MQTT data thread")
            self.continueFlag.set()
        else:
            print("Starting MQTT data thread")
            self.mqttclient.loop()
            #thread(self._sendAll, enableConditionMO, period)
            self._sendAll(enableConditionMO, period)
        
        
    def _sendAll(self, enableConditionMO, period, errorLimit = 5):
        self.sending = True
        errorCount = 0
        while enableConditionMO.get() and errorCount < errorLimit: # {
            try: 
                if not self.continueFlag.is_set():
                    print("MQTT data thread suspended")
                
                self.continueFlag.wait()
                
                for key in self.dataCenter.sensorStorage:
                    nDecimals = self.dataCenter.decimalPos[key].get()
                    data = self.dataCenter.sensorStorage[key].get()
                    shortString = str('%.*f') % (nDecimals, data)
                    print(shortString)
                    self.mqttclient.publish(str("roomIOT2021" + '/' + key), shortString, self.preferredQoS.get())
            
                sleep(period)
            except Exception as e:
                print("MQTT Data process - Error! : ")
                print(e)
                errorCount += 1
                self.mqttclient.reconnect()
                sleep(200)
        #}
    
        print("Stopping MQTT thread...")
        
        if errorCount >= errorLimit:
            glob.lcd.lock.acquire()
            print("Too many errors.")
            glob.lcd.clear()
            glob.lcd.writeCGRAM(chars.SAD_FACE, 7) #Temp buffer --> #SAD
            glob.lcd.printLine("MQTT connection\ncrashed. " + glob.lcd.CGRAM[7])
            sleep(2000)
            glob.lcd.clear()
            glob.lcd.lock.release()
            self.controlCenter.dashboard.displayStatus()
            
        self.sending = False