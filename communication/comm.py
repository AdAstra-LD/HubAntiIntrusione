from wireless import wifi
from mqtt import mqtt

# import wifi support
from espressif.esp32net import esp32wifi as wifi_driver

import streams
import glob

wifi_driver.auto_init()

class AlarmComm():
    def __init__(self, alarmControlCenter, networkName, password, attempts = 5):
        self.controlCenter = alarmControlCenter
        streams.serial()
        
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
                    glob.lcd.printLine("WiFi connection\nfailed.")
                    sleep(4000)
                    glob.lcd.clear()
                    glob.lcd.lock.release()
                    self.controlCenter.dashboard.displayStatus()
                    return
                sleep(500)
        
        self.controlCenter.running["wifi"].set(True)
        
        #try:
        client = mqtt.Client("Test", clean_session = True)
        for retry in range(attempts):
            try:
                print("Attempting connection with MQTT broker...")
                client.connect("broker.mqtt-dashboard.com", keepalive = 20)
                break
            except Exception as e:
                print("MQTT connection error: ", e)
                
                if (retry == attempts-1):
                    glob.lcd.lock.acquire()
                    print("Too many errors. Not gonna try anymore.")
                    glob.lcd.clear()
                    glob.lcd.printLine("MQTT connection\nfailed.")
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