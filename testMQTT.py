
import streams

# import the wifi interface
from wireless import wifi

from mqtt import mqtt

# import wifi support
from espressif.esp32net import esp32wifi as wifi_driver

streams.serial()

# init the wifi driver
wifi_driver.auto_init()


sleep(5000)
print("Establishing Link...")
try:
   
    wifi.link("Vodafone-33577254",wifi.WIFI_WPA2,"FamigliaMacaro4")
    #wifi.link("ONEPLUS_co_apawdv",wifi.WIFI_WPA2,"alessandro")
    print("Link Established")
except Exception as e:
    print("ooops, something wrong while linking :(", e)
    while True:
        sleep(1000)

def manage_system(client,data):
    message = data['message']
    print("Sample received: ", message.payload)

#def print_other(client,data):
#   message = data['message']
#   print("Topic: ", message.topic)
#   print("Payload received: ", message.payload)

def send_temp(obj):
    print("publishing temperature: ", obj)
    client.publish("stanza/temperatura", str(obj), 1)
   
#def publish_to_self():
    #client.publish("desktop/others","hello! "+str(random(0,10)))

#def rec_ping():
    #print("received a PINGREQ message from the server")

#def pub_comp():
   # print("publication successfully completed")


try:
    
    client = mqtt.Client("zerynth-mqtt-test",True)
    for retry in range(5):
        try:
            client.connect("test.mosquitto.org", 30)
            break
        except Exception as e:
            print("connecting to mosquitto...")
    print("connected to mosquitto.")
    
    # subscribe to channels
    client.subscribe([["sistema/attivazione",2]])
    client.subscribe([["casa/temperatura",1]])
    #client.subscribe([["desktop/others",2]])
    
    # configure callbacks for "PUBLISH" message
    # on serve a settare una callback in risposta a un comando mqtt
    # client.on(command, function, condition=None, priority=0)
    # possono essere mqtt.PUBLISH per la pubblicazione
    client.on(mqtt.PUBLISH,manage_system)
    
    # configure callbacks for "PINGREQ" message
    # PINGREQ è inviato dal Client al Server
    #client.on(mqtt.PINGREQ, rec_ping)
    
    # configure callbacks for "PUBCOMP" message
    #client.on(mqtt.PUBCOMP, pub_comp)
    #client.set_will('temp/random', "testamento", 2, False)
    # start the mqtt loop
    client.loop()
    
    while True:
       sleep(5000)
       x = random(0,50)
       send_temp(x)
except Exception as e:
    sleep(100)
    
    