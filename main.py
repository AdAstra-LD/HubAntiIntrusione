# Test Infrared Sensor
# Created at 2021-04-22 16:04:22.591934

import streams
import threading

import pwm
import i2c

import display.LCDI2C as lcdi2c
import display.specialChars as chars
import display.localDashboard as ui

import userinput.settings as settings
import userinput.keypad as keypad
import communication.comm as comm

import alarm.led as led
import alarm.buzzer as buzzer
import glob

pinBuzzer = D15.PWM
#pinPhotoresist = A2

pinIR = D5
pinEnButton = D21
#pinSettingsButton = D2


def initIO():
    streams.serial()
    
    glob.lcd = initLCD(I2C1)
    
    glob.pad = keypad.KeyPad(invert = True)
    
    print("Setting up glob.ledRGB...")
    glob.ledRGB = led.RGBLed(D4, D22, D23) #R, G, B
    glob.ledRGB.RGBoff()
    
    print("Setting up buzzer...")
    glob.buzzer = buzzer.Buzzer(pinBuzzer)
    
    print("Setting up input pins...")
    pinMode(pinIR, INPUT)
    #pinMode(pinPhotoresist, INPUT)
    #pinMode(pinSettingsButton, INPUT_PULLDOWN)
    pinMode(pinEnButton, INPUT_PULLUP)
    
    glob.lcd.printLine("Unisa - IOT 2021\nLaiso, Macaro", align = "C")
    sleep(750)
    print("Setup completed")
    settings.load()
    ui.showDashboard(glob.lcd)
    
    #comm.AlarmComm("FASTWEB-RML2.4", "marcheselaiso@2020 2.4")
    #thread(readAmbientLight)

def toggleOnOff():
    status = glob.enable["alarm"].get()
    
    glob.enable["alarm"].set(not status)
    glob.enable["audio"].set(not status)
    glob.enable["flash"].set(not status)
    
    glob.lcdLock.release() #takes priority over every other process
    glob.lcdLock.acquire()
    glob.lcd.clear()

    if (glob.enable["alarm"].get() == True):
        glob.ledRGB.RGBset(0, 0, 1)
        print("Sistema abilitato")
        glob.lcd.printAtPos(glob.lcd.CGRAM[4], glob.lcd.nCols-1, 0) #EXCLAMATION
    else:
        glob.ledRGB.memorizeColor(0, 0, 0)
        stopAlarm()
        glob.ledRGB.RGBoff()
        glob.lcd.printAtPos(' ', glob.lcd.nCols-1, 0)
        print("Sistema disabilitato")
        
    glob.lcdLock.release()

def intrusione():
    if (glob.enable["alarm"].get() == True):
        glob.ledRGB.flash(flashFrequency = 20, color = 'R')
        #glob.buzzer.play()
        print("Intrusione!!!")
        glob.lcdLock.acquire()
        glob.lcd.printLine("!  Intruder  !", 1, align = "CENTER")
    else:
        print("Movimento rilevato... ma l'allarme non e' inserito")
        glob.lcdLock.acquire()
        glob.lcd.printLine("Alarm busy...", 1, align = "CENTER")

def stopAlarm():
    print("Alarm signal down...")
    glob.lcd.clear()
    glob.lcdLock.release()
    
    glob.enable["audio"].set(False)
    glob.enable["flash"].set(False)
        
def initLCD(port = I2C0):
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
#PINS MUST BE ALREADY INITIALIZED, BEFORE THESE INTERRUPTS ARE SET UP

onPinFall(pinEnButton, toggleOnOff)
#onPinRise(pinSettingsButton, settings.userSetup)
onPinRise(pinIR, intrusione)
onPinFall(pinIR, stopAlarm)
