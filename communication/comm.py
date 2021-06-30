from wireless import wifi
from mqtt import mqtt

# import wifi support
from espressif.esp32net import esp32wifi as wifi_driver
import threading
import utilities.mutableObject as mo
import peripherals.specialChars as chars
import glob

wifi_driver.auto_init()

class CommCenter():
    def __init__(self, alarmDataCenter, networkName, password, attempts = 5, preferredQoS = 1):
        self.dataCenter = alarmDataCenter
        
        self.continueFlag = threading.Event()
        self.continueFlag.set()
        
        self.enableMQTTsend = True
        self.running = { 
            #Global Vars for system processes
            "wifi" : False,
            "mqtt" : False,
            "mqttSend" : False,
        }
        
        self.preferredQoS = preferredQoS
        
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
                    return
                sleep(500)
        
        self.running["wifi"] = True
        
        #try:
        self.mqttclient = mqtt.Client("Test", clean_session = True)
        for retry in range(attempts):
            try:
                print("Attempting connection with MQTT broker...")
                self.mqttclient.connect("192.168.1.67", port=1886, keepalive = 15)
                print("MQTT connection successful.")
                break
            except Exception as e:
                print("MQTT connection error: ", e)
                
                if retry == attempts-1:
                    glob.lcd.lock.acquire()
                    print("Too many errors. Not gonna try anymore.")
                    glob.lcd.clear()
                    glob.lcd.writeCGRAM(chars.SAD_FACE, 7) #Temp buffer --> #SAD
                    glob.lcd.printLine("MQTT connection\nfailed. " + glob.lcd.CGRAM[7])
                    sleep(4000)
                    glob.lcd.clear()
                    glob.lcd.lock.release()
                    return
                sleep(500)
        
        self.mqttclient.set_will('roomIOT2021/#', str("Error"), 2, True)
        self.running["mqtt"] = True
        #except Exception as e:
        #    sleep(150)
    
    def dataSendLoop(self, period, nonBlocking = False):
        self.enableMQTTsend = True
        
        if self.running["mqttSend"]:
            print("Resuming MQTT data thread")
            self.continueFlag.set()
        else:
            print("Starting MQTT data thread")
            self.mqttclient.loop()
            
            if nonBlocking:
                thread(self._sendAll, period)
            else:
                self._sendAll(period)
        
        
    def _sendAll(self, period, errorLimit = 5):
        self.running["mqttSend"] = True
        for retry in range(errorLimit):
            try: 
                while self.enableMQTTsend: # {
                    self.continueFlag.wait()
    
                    self.dataCenter.sensoreStorageLock.acquire()
                    print("Sending data")
                    for key in self.dataCenter.sensorStorage:
                        nDecimals = self.dataCenter.decimalPos[key].get()
                        data = self.dataCenter.sensorStorage[key].get()
                        shortString = str('%.*f') % (nDecimals, data)
                        #print(shortString)
                        self.mqttclient.publish(str("roomIOT2021" + '/' + key), shortString, self.preferredQoS)
                    self.dataCenter.sensoreStorageLock.release()
                    sleep(period)
                # }
                break
            except Exception as e:
                print("MQTT Data process: " + str(e))
                if retry == errorLimit-1:
                    glob.lcd.lock.acquire()
                    print("Too many errors.")
                    glob.lcd.clear()
                    glob.lcd.writeCGRAM(chars.SAD_FACE, 7) #Temp buffer --> #SAD
                    glob.lcd.printLine("MQTT connection\ncrashed. " + glob.lcd.CGRAM[7])
                    sleep(2000)
                    glob.lcd.clear()
                    glob.lcd.lock.release()
                    return
                #self.mqttclient.reconnect()
                sleep(200)
    
        print("Stopping MQTT thread...")
        self.running["mqttSend"] = False