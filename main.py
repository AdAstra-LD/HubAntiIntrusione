# Test Infrared Sensor
# Created at 2021-04-22 16:04:22.591934

import streams
import threading

import pwm
import i2c

import peripherals.LCDI2C as lcdi2c
import peripherals.led as led
import peripherals.buzzer as buzzer
import peripherals.specialChars as chars
import peripherals.keypad as keypad

import communication.comm as comm

import alarm.controlcenter as cc
import alarm.datacenter as dc
import alarm.localDashboard as ui
import alarm.settings as settings
import glob

from meas.htu21d import htu21d
#pinPhotoresist = A2

pinIR = D5
pinEnButton = D21

htu21dconfig_attempts = 5
runDashboardFlag = False

import utilities.circularList as cl

def initIO():
    global runDashboardFlag
    streams.serial()
    
    glob.lcd = initLCD(I2C1)
    glob.pad = keypad.KeyPad(invert = True)
    
    glob.htu21d = htu21d.HTU21D(I2C0)
    for retry in range(5):
        try:
            glob.htu21d.start()
            sleep(500)
            glob.htu21d.init()
            sleep(500)
            runDashboardFlag = True
            break
        except Exception as e:
            print(e)
    
    print("Setting up input pins...")
    pinMode(pinIR, INPUT)
    #pinMode(pinPhotoresist, INPUT)
    
    pinMode(pinEnButton, INPUT_PULLUP)
    print("Setup completed")
        
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

initIO()

glob.lcd.printLine("Unisa - IOT 2021\nLaiso, Macaro", align = "C")

ledRGB = led.RGBLed(D4, D22, D23)
ledRGB.rainbowFade(duration = 500, times = 2)

sleep(100)
ledRGB.RGBset(R = 1, G = 1)
prefs = settings.UserSettings(glob.lcd, glob.pad, ledRGB)

alarmDataCenter = dc.DataCenter(glob.htu21d, decimalTemperature = 2, decimalHumidity = 2, decimalLight = 1)
alarmCommunicationCenter = comm.CommCenter(alarmDataCenter, "FASTWEB-RML2.4", "marcheselaiso@2020 2.4")
alarmControlCenter = cc.ControlCenter(alarmDataCenter, alarmCommunicationCenter, glob.lcd, ledRGB, buzzer.Buzzer(D15.PWM), pinEnButton, pinIR)
localDashboard = ui.LocalDashboard(alarmDataCenter, alarmControlCenter, glob.lcd)
alarmControlCenter.dashboard = localDashboard

ledRGB.RGBoff()

alarmDataCenter.startRetrieveData(5000)
if runDashboardFlag:
    localDashboard.show(5000)
    
alarmCommunicationCenter.dataSendLoop(5000, nonBlocking = False)#