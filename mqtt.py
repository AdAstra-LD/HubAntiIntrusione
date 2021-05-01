# testMQTT
# Created at 2021-05-01 13:43:08.132766

import streams

#import a module to access a net driver (wifi)
from wireless import wifi

#import a module for MQTT protocol
from mqtt import mqtt

#import the actual net driver for the specific board 
from from espressif.esp32net import esp32wifi as wifi_driver

streams.serial()

#init the wifi_driver
wifi_driver.auto_init()

sleep(5000)
print("Aspetto il collegamento...")
try:
    wifi.link("Vodafone-33577254", wifi.WIFI_WPA2, "FamigliaMacaro4")
    print("Collegamento effettuato con successo!")
except Exception:
    print("Qualcosa è andato storto..")
    while True:
        sleep(1000)
        
        ciao

        
    
    
