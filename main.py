# Test Infrared Sensor
# Created at 2021-04-22 16:04:22.591934

import streams
import threading

import pwm
import i2c

import glob
import peripherals.LCDI2C as lcdi2c
import peripherals.htu21d as htu21d
import peripherals.led as led
import peripherals.buzzer as buzzer
import peripherals.keypad as keypad

import alarm.controlcenter as cc
import alarm.datacenter as dc
import alarm.settings as settings

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
    lcdObj.writeCGRAM(lcdi2c.TEMPERATURE, 0)
    lcdObj.writeCGRAM(lcdi2c.HUMIDITY, 1)
    lcdObj.writeCGRAM(lcdi2c.LIGHT, 2)
    lcdObj.writeCGRAM(lcdi2c.CELSIUS, 3)
    lcdObj.writeCGRAM(lcdi2c.MQTT, 4)
    lcdObj.writeCGRAM(lcdi2c.WIFI, 5)
    lcdObj.writeCGRAM(lcdi2c.NO_SIGNAL, 6)
    lcdObj.writeCGRAM(lcdi2c.SMILEY_FACE, 7) #this acts as a temp buffer
    
    return lcdObj
    

streams.serial()

ledRGB = led.RGBLed(D4, D22, D23)
buzz = buzzer.Buzzer(D15.PWM)
buzz.playSequence(music.waitTone, BPM = 240)
    
lcd = initLCD(I2C1)
lcd.printLine("UniSa - IOT 2021\nLaiso, Macaro", align = "C")
ledRGB.rainbowFade(duration = 500, times = 2)
pad = keypad.KeyPad(invert = True)

htu = htu21d.HTU21D(I2C0, clk = 125000)
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

sleep(100)
ledRGB.RGBset(R = 255, G = 255)
prefs = settings.UserSettings(lcd, pad, ledRGB, buzz)

if digitalRead(pinEnButton) == LOW: #hard reset menu
    prefs.resetAll()

lcd.lock.acquire()
lcd.writeCGRAM(lcdi2c.SAD_FACE, 7) #Temp buffer --> #SAD
lcd.lock.release()

mqttClient = mqtt.Client("ESP32_IOT_GL", clean_session = True)
mqttLock = threading.Lock()
alarmDataCenter = dc.DataCenter(htu, pinPhotoresistor, lcd, decimalTemperature = 2, decimalHumidity = 2, decimalLight = 1)
alarmControlCenter = cc.ControlCenter(prefs, alarmDataCenter, lcd, ledRGB, buzz, pinEnButton, pinIR)
alarmControlCenter.linkAndStartComm("RML_FW-2.4", "RaimoMarcheseLaiso@2021 2.4GHz", mqttClient, mqttLock, "broker.mqtt-dashboard.com", port = 1883, attempts = 5)

if alarmControlCenter.wifiOk and alarmControlCenter.MQTTOk:
    alarmDataCenter.linkMQTTClient(mqttClient, mqttLock)
    ledRGB.linkMQTTClient(mqttClient, glob.topicRoot + '/' + 'ledRGB')
    
    
ledRGB.RGBset(0, 0, 0)
alarmControlCenter.enableIO()

sleep(900)
lcd.lock.acquire()
lcd.clear()
sleep(200)
buzz.playSequence(music.warningTone, BPM = 300)
ledRGB.memorizeCurrentColor()
ledRGB.quickBlink(R=255, G=255, B = 0)
lcd.printLine("Remember to wait\n30 - 45 seconds\nbefore using the\ninfrared sensor.", sentenceDelay = 1500, align = "L")
lcd.lock.release()
ledRGB.restoreColor()
sleep(500)
lcd.clear()
buzz.playSequence(music.sequenceStartTone, BPM = 240)
ledRGB.quickBlink(R=0, G=255, B = 0)

lcd.clear()
alarmControlCenter.checkSensorBusy()
alarmControlCenter.displayStatus()
alarmDataCenter.startRetrieveData(1750)#