# Test Infrared Sensor
# Created at 2021-04-22 16:04:22.591934

import streams
import threading

import pwm
import i2c

import glob
import peripherals.LCDI2C as lcdi2c
import peripherals.led as led
import peripherals.buzzer as buzzer
import peripherals.specialChars as chars
import peripherals.keypad as keypad

import alarm.controlcenter as cc
import alarm.datacenter as dc
import alarm.settings as settings

import peripherals.htu21d as htu21d
import utilities.music as music
from mqtt import mqtt

pinIR = D5
pinEnButton = D21
pinEnButton = D21
pinPhotoresistor = A2

htu21dconfig_attempts = 5

import utilities.circularList as cl
lcd = None
pad = None
htu = None

def initLCD(port = I2C1):
    lcdObj = lcdi2c.LCDI2C(port, nCols=16, nRows=2)
    if (port == None):
        return lcdObj
    
    lcdObj.prepare()
    lcdObj.writeCGRAM(chars.TEMPERATURE, 0)
    lcdObj.writeCGRAM(chars.HUMIDITY, 1)
    lcdObj.writeCGRAM(chars.LIGHT, 2)
    lcdObj.writeCGRAM(chars.CELSIUS, 3)
    lcdObj.writeCGRAM(chars.EXCLAMATION, 4)
    lcdObj.writeCGRAM(chars.UNLOCKED, 5)
    lcdObj.writeCGRAM(chars.WIFI, 6)
    #lcdObj.writeCGRAM(chars.LOCKED, 7) #this acts as a temp buffer
    
    return lcdObj
    

streams.serial()

ledRGB = led.RGBLed(D4, D22, D23)
buzz = buzzer.Buzzer(D15.PWM)
buzz.playSequence(music.waitTone, BPM = 240)
    
lcd = initLCD(I2C1)
lcd.printLine("UniSa - IOT 2021\nLaiso, Macaro", align = "C")
pad = keypad.KeyPad(invert = True)

htu = htu21d.HTU21D(I2C0, clk = 150000)
for retry in range(5):
    try:
        htu.start()
        sleep(500)
        htu.init(res = 0)
        sleep(500)
        break
    except Exception as e:
        print(e)

print("Setting up input pins...")
pinMode(pinIR, INPUT)
pinMode(pinPhotoresistor, INPUT)

pinMode(pinEnButton, INPUT_PULLUP)
print("Setup completed")

ledRGB.rainbowFade(duration = 500, times = 2)

sleep(100)
ledRGB.RGBset(R = 255, G = 255)
prefs = settings.UserSettings(lcd, pad, ledRGB, buzz)
prefs.userSetup()

mqttClient = mqtt.Client("ESP32_IOT_GL", clean_session = True)
alarmDataCenter = dc.DataCenter(htu, pinPhotoresistor, lcd, decimalTemperature = 2, decimalHumidity = 2, decimalLight = 1)
alarmControlCenter = cc.ControlCenter(alarmDataCenter, lcd, ledRGB, buzz, pinEnButton, pinIR)
alarmControlCenter.linkAndStartComm("FASTWEB-RML2.4", "marcheselaiso@2020 2.4", mqttClient, "broker.mqtt-dashboard.com", port = 1883, attempts = 5)

if alarmControlCenter.wifiOk and alarmControlCenter.MQTTOk:
    alarmDataCenter.mqttClient = mqttClient
    alarmControlCenter.mqttClient = mqttClient
    ledRGB.linkMQTTClient(mqttClient, glob.topicRoot + '/' + 'ledRGB')
    buzz.linkMQTTClient(mqttClient, glob.topicRoot + '/' + 'buzzer')
    
    
ledRGB.RGBset(0, 0, 0)
buzz.sendStatus()

lcd.printLine("Remember to wait\n30 - 45 seconds\nbefore using the\ninfrared sensor.", sentenceDelay = 1500, align = "L")
sleep(1000)
lcd.clear()
alarmControlCenter.checkBusy()
buzz.playSequence(music.sequenceStartTone, BPM = 240)

alarmControlCenter.displayStatus()
alarmDataCenter.startRetrieveData(1500)#