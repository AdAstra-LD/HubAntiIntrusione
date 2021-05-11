from wireless import wifi
from mqtt import mqtt

# import wifi support
from espressif.esp32net import esp32wifi as wifi_driver

import threading
import streams

wifi_driver.auto_init()

class AlarmComm():
    def __init__(self, networkName, password, attempts = 6):
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
                    print("Not gonna try anymore.")
                    return
                    
                sleep(500)
        
        try:
            client = mqtt.Client("Test",True)
            for retry in range(attempts):
                try:
                    print("Attempting connection with MQTT broker...")
                    client.connect("broker.mqtt-dashboard.com", 30)
                    print("MQTT connection successful.")
                    break
                except Exception as e:
                    print("MQTT connection error: ", e)
                    
                    if (retry == attempts-1):
                        print("Not gonna try anymore.")
                        return
                    sleep(500)
                    
            print(".")
        except Exception as e:
            sleep(150)
    
    def runThreadedTask(self, task):
        thread(task)